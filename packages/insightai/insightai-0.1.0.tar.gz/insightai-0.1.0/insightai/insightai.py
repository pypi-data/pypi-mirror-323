import os
from contextlib import redirect_stdout
import io
import re
import time
import pandas as pd
import warnings
import traceback
import sys
import json
warnings.filterwarnings('ignore')

try:
    # Attempt package-relative import
    from . import models, prompts, func_calls, reg_ex, log_manager, output_manager, utils
except ImportError:
    # Fall back to script-style import
    import models, prompts, func_calls, reg_ex, log_manager, output_manager, utils

class InsightAI:
    def __init__(self, df: pd.DataFrame = None,
             db_path: str = None,
             max_conversations: int = 4,
             debug: bool = False, 
             exploratory: bool = True,
             df_ontology: bool = False):
        
        if db_path:
            import sqlite3
            self.conn = sqlite3.connect(db_path)
            self.cur = self.conn.cursor()
        self.df = df if df is not None else None
        
        # Output
        self.output_manager = output_manager.OutputManager()

        # Check if the OPENAI_API_KEY environment variable is set
        if not os.getenv('OPENAI_API_KEY'):
            raise EnvironmentError("OPENAI_API_KEY environment variable not found.")
        
        # Check if the GROQ_API_KEY environment variable is set
        if not os.getenv('GROQ_API_KEY'):
            raise EnvironmentError("GROQ_API_KEY environment variable not found.")

        self.MAX_ERROR_CORRECTIONS = 5
        # Set the maximum number of question/answer pairs to be kept in the conversation memory
        self.MAX_CONVERSATIONS = (max_conversations*2) - 1
        
        # Dataframe
        self.df = df if df is not None else None
        self.original_df_columns = df.columns.tolist() if df is not None else None
        self.df_ontology = df_ontology
        self.query_metrics = None
        
        # Results of the code execution
        self.code_exec_results = None

        # Debug and exploratory modes
        self.debug = debug
        self.exploratory = exploratory
        
        # Prompts
        # Define list of templates
        templates = [
            "default_example_output_df",
            "default_example_output_gen",
            "default_example_output_sql",
            "default_example_plan_sql",
            "sql_generator_system",
            "sql_generator_user_sql",
            "code_generator_system_sql", 
            "code_generator_user_sql",
            "default_example_plan_df",
            "default_example_plan_gen",
            "expert_selector_system",
            "expert_selector_user",
            "analyst_selector_system",
            "analyst_selector_user",
            "planner_system",
            "planner_user_gen",
            "planner_user_df",
            "theorist_system",
            "dataframe_inspector_system",
            "google_search_query_generator_system",
            "google_search_react_system",
            "code_generator_system_df",
            "code_generator_system_gen",
            "code_generator_user_df",
            "code_generator_user_gen",
            "error_corector_system",
            "code_debugger_system",
            "code_ranker_system",
            "solution_summarizer_system"
        ]

        prompt_data = {}

        # Check if the JSON file exists
        if os.path.exists("PROMPT_TEMPLATES.json"):
            # Load from JSON file
            with open("PROMPT_TEMPLATES.json", "r") as f:
                prompt_data = json.load(f)

        # Set templates to the values from the JSON file or the default values. This dynamicaly sets the object attributes.
        # These attributes are part of the object's state and will exist as long as the object itself exists.
        # The attributes can be called using self.<attribute_name> throughout the class.
        for template in templates:
            value = prompt_data.get(template, getattr(prompts, template, ""))
            setattr(self, template, value)

        # Regular expresions
        self._extract_code = reg_ex._extract_code
        self._extract_rank = reg_ex._extract_rank
        self._extract_expert = reg_ex._extract_expert
        self._extract_analyst = reg_ex._extract_analyst
        self._extract_plan = reg_ex._extract_plan
        self._remove_examples = reg_ex._remove_examples

        # Functions
        self.task_eval_function = func_calls.task_eval_function
        self.insights_function = func_calls.solution_insights_function
        # LLM calls
        self.llm_call = models.llm_call
        self.llm_stream = models.llm_stream

        # Logging
        self.token_cost_dict = {
                'gpt-4o': {'prompt_tokens': 0.0025, 'completion_tokens': 0.01},
                'gpt-4o-2024-11-20': {'prompt_tokens': 0.0025, 'completion_tokens': 0.01},
                'gpt-4o-2024-08-06': {'prompt_tokens': 0.0025, 'completion_tokens': 0.01},
                'gpt-4o-mini': {'prompt_tokens': 0.00015, 'completion_tokens': 0.0006},
                'gpt-4o-mini-2024-07-18': {'prompt_tokens': 0.00015, 'completion_tokens': 0.0006},
                'o1': {'prompt_tokens': 0.015, 'completion_tokens': 0.06},
                'o1-2024-12-17': {'prompt_tokens': 0.015, 'completion_tokens': 0.06},
                'o1-preview': {'prompt_tokens': 0.015, 'completion_tokens': 0.06},
                'o1-preview-2024-09-12': {'prompt_tokens': 0.015, 'completion_tokens': 0.06},
                'o1-mini': {'prompt_tokens': 0.003, 'completion_tokens': 0.012},
                'o1-mini-2024-09-12': {'prompt_tokens': 0.003, 'completion_tokens': 0.012},
                'chatgpt-4o-latest': {'prompt_tokens': 0.005, 'completion_tokens': 0.015},
                'gpt-4-turbo': {'prompt_tokens': 0.01, 'completion_tokens': 0.03},
                'gpt-4-turbo-2024-04-09': {'prompt_tokens': 0.01, 'completion_tokens': 0.03},
                'gpt-4': {'prompt_tokens': 0.03, 'completion_tokens': 0.06},
                'gpt-4-32k': {'prompt_tokens': 0.06, 'completion_tokens': 0.12},
                'gpt-4-0125-preview': {'prompt_tokens': 0.01, 'completion_tokens': 0.03},
                'gpt-4-1106-preview': {'prompt_tokens': 0.01, 'completion_tokens': 0.03},
                'gpt-4-vision-preview': {'prompt_tokens': 0.01, 'completion_tokens': 0.03},
                'gpt-3.5-turbo-0125': {'prompt_tokens': 0.0005, 'completion_tokens': 0.0015},
                'gpt-3.5-turbo-instruct': {'prompt_tokens': 0.0015, 'completion_tokens': 0.002},
                'gpt-3.5-turbo-1106': {'prompt_tokens': 0.001, 'completion_tokens': 0.002},
                'gpt-3.5-turbo-0613': {'prompt_tokens': 0.0015, 'completion_tokens': 0.002},
                'gpt-3.5-turbo-16k-0613': {'prompt_tokens': 0.003, 'completion_tokens': 0.004},
                'davinci-002': {'prompt_tokens': 0.002, 'completion_tokens': 0.002},
                'babbage-002': {'prompt_tokens': 0.0004, 'completion_tokens': 0.0004},
                'llama-3.2-1b-preview': {'prompt_tokens': 0.00004, 'completion_tokens': 0.00004},
                'llama-3.2-3b-preview': {'prompt_tokens': 0.00006, 'completion_tokens': 0.00006},
                'llama-3.3-70b-versatile': {'prompt_tokens': 0.00059, 'completion_tokens': 0.00079},
                'llama-3.1-8b-instant': {'prompt_tokens': 0.00005, 'completion_tokens': 0.00008},
                'llama-3-70b': {'prompt_tokens': 0.00059, 'completion_tokens': 0.00079},
                'llama-3-8b': {'prompt_tokens': 0.00005, 'completion_tokens': 0.00008},
                'mixtral-8x7b-instruct': {'prompt_tokens': 0.00024, 'completion_tokens': 0.00024},
                'gemma-7b-instruct': {'prompt_tokens': 0.00007, 'completion_tokens': 0.00007},
                'gemma-2-9b': {'prompt_tokens': 0.00020, 'completion_tokens': 0.00020},
                'llama-3-groq-70b-preview': {'prompt_tokens': 0.00089, 'completion_tokens': 0.00089},
                'llama-3-groq-8b-preview': {'prompt_tokens': 0.00019, 'completion_tokens': 0.00019},
                'llama-guard-3-8b': {'prompt_tokens': 0.00020, 'completion_tokens': 0.00020},
                'llama-3.2-11b-vision': {'prompt_tokens': 0.00018, 'completion_tokens': 0.00018},
                'llama-3.2-90b-vision': {'prompt_tokens': 0.00090, 'completion_tokens': 0.00090}
            }
        self.log_and_call_manager = log_manager.LogAndCallManager(self.token_cost_dict)
        self.chain_id = None

        # Messages lists
        self.pre_eval_messages = [{"role": "system", "content": self.expert_selector_system}]
        self.select_analyst_messages = [{"role": "system", "content": self.analyst_selector_system}]
        self.eval_messages = [{"role": "system", "content": self.planner_system.format(utils.get_readable_date())}]
        self.code_messages = [{"role": "system", "content": self.code_generator_system_df}]
    ######################
    ### Util Functions ###
    ######################

    def reset_messages_and_logs(self):
        self.pre_eval_messages = [{"role": "system", "content": self.expert_selector_system}]
        self.select_analyst_messages = [{"role": "system", "content": self.analyst_selector_system}]
        self.eval_messages = [{"role": "system", "content": self.planner_system.format(utils.get_readable_date())}]
        self.code_messages = [{"role": "system", "content": self.code_generator_system_df}]
        self.code_exec_results = None

        self.log_and_call_manager.clear_run_logs()

    def messages_maintenace(self, messages):
        # Remove tool_calls messages from the messages list
        for i in range(len(messages) - 1, -1, -1):  # Start from the last item to index 0
            msg = messages[i]
            if "tool_calls" in msg or msg.get("role") == "tool":
                messages.pop(i)
        # Remove the oldest conversation from the messages list
        if len(messages) > self.MAX_CONVERSATIONS:
            messages.pop(1)
            messages.pop(1)
            self.output_manager.display_system_messages("Truncating messages")
    
    ######################
    ### Eval Functions ###
    ######################
    
    def select_expert(self, pre_eval_messages, file_type):
        '''Call the Expert Selector'''
        agent = 'Expert Selector'
        using_model, provider = models.get_model_name(agent)

        self.output_manager.display_tool_start(agent, using_model)

        # Append file type to last message
        pre_eval_messages[-1]['content'] += f"\nFile type: {file_type}"

        llm_response = self.llm_stream(self.log_and_call_manager, 
                                    pre_eval_messages, 
                                    agent=agent,
                                    chain_id=self.chain_id)
                                    
        expert, requires_dataset, confidence = self._extract_expert(llm_response)
        return expert, requires_dataset, confidence
    def _extract_sql_query(self, response: str) -> str:
        """Extract and clean SQL queries from the LLM response.
        
        Args:
            response (str): The LLM response containing SQL code blocks
            
        Returns:
            str: Extracted SQL query with comments and whitespace cleaned
        """
        # Match any standalone SQL code without markdown tags
        sql_pattern = re.compile(r'^[^`]+$', re.MULTILINE)
        query_matches = sql_pattern.findall(response)
        
        if query_matches:
            # Concatenate and clean queries
            query = " ".join(query_matches)
            query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)  # Remove comments
            query = '\n'.join(line for line in query.split('\n') if line.strip())  # Remove empty lines
            return query.strip()
        return None

    def select_analyst(self, select_analyst_messages):
        '''Call the Analyst Selector'''
        agent = 'Analyst Selector'
        # Call OpenAI API to evaluate the task
        llm_response = self.llm_stream(self.log_and_call_manager,select_analyst_messages, agent=agent, chain_id=self.chain_id)
        analyst, query_unknown, query_condition = self._extract_analyst(llm_response)

        return analyst, query_unknown, query_condition
    
    def task_eval(self, eval_messages, agent):
        '''Call the Task Evaluator'''
        using_model,provider = models.get_model_name(agent)

        self.output_manager.display_tool_start(agent,using_model)

        # Call OpenAI API to evaluate the task
        llm_response = self.llm_stream(self.log_and_call_manager,eval_messages, agent=agent, chain_id=self.chain_id)

        self.output_manager.display_task_eval(llm_response)

        if agent == 'Planner':
            response = self._extract_plan(llm_response)
        else:
            response = llm_response
            
        return response
    
    def taskmaster(self, question, df_columns):
        plan = None
        analyst = None
        query_unknown = None
        query_condition = None
        requires_dataset = None
        confidence = None
        agent = None
        file_type = '.db' if hasattr(self, 'conn') else '.csv'
        print(f"Detected file type: {file_type}")

        # Modify expert selection for .db files
        if file_type == '.db':
            expert = 'SQL Analyst'
            requires_dataset = True
            confidence = 9
        else:
            self.pre_eval_messages.append({"role": "user", "content": self.expert_selector_user.format(question)})
            expert, requires_dataset, confidence = self.select_expert(self.pre_eval_messages, file_type)
            self.pre_eval_messages.append({"role": "assistant", "content": f"expert:{expert},requires_dataset:{requires_dataset},confidence:{confidence}"})

        if expert == 'SQL Analyst':
            agent = 'SQL Generator'
            schema = self.get_db_schema()
            if schema:
                self.eval_messages.append({"role": "user", "content": f"Database Schema:\n{schema}\n\nQuery: {question}"})

        elif expert == 'Data Analyst':
            self.select_analyst_messages.append({"role": "user", "content": self.analyst_selector_user.format(None if self.df is None else df_columns, question)})
            analyst, query_unknown, query_condition = self.select_analyst(self.select_analyst_messages)
            self.select_analyst_messages.append({"role": "assistant", "content": f"analyst:{analyst},unknown:{query_unknown},condition:{query_condition}"})

            if analyst == 'Data Analyst DF':
                agent = 'Planner'
                example_plan = self.default_example_plan_df
                if self.df_ontology:
                    self.query_metrics = utils.inspect_dataframe(self.df, self.log_and_call_manager, self.chain_id, query_condition)
                    self.query_metrics = self._extract_plan(self.query_metrics)
                    dataframe_description = f"{self.df.head(3)}\n\nREQUIRED METRICS AND JOINS:\n```yaml\n{self.query_metrics}\n```"
                else:
                    dataframe_description = utils.inspect_dataframe(self.df)
                self.eval_messages.append({"role": "user", "content": self.planner_user_df.format(question, None if self.df is None else dataframe_description, example_plan)})
                self.code_messages[0] = {"role": "system", "content": self.code_generator_system_df}
            
            elif analyst == 'Data Analyst Generic':
                agent = 'Planner'
                example_plan = self.default_example_plan_gen
                self.eval_messages.append({"role": "user", "content": self.planner_user_gen.format(question, example_plan)})
                self.code_messages[0] = {"role": "system", "content": self.code_generator_system_gen}

        else:
            agent = 'Research Specialist'
            self.eval_messages.append({"role": "user", "content": self.theorist_system.format(utils.get_readable_date(),question)})

        task_eval = self.task_eval(self.eval_messages, agent)
        self.eval_messages.append({"role": "assistant", "content": task_eval})
        self.messages_maintenace(self.eval_messages)

        if expert in ['Research Specialist', 'SQL Analyst']:
            self.log_and_call_manager.print_summary_to_terminal()
        elif expert == 'Data Analyst':
            plan = task_eval

        return analyst, plan, query_unknown, query_condition, requires_dataset, confidence
    #####################
    ### Main Function ###
    #####################

    def pd_agent_converse(self, question=None):
        if question is not None:
            loop = False
        else:
            loop = True

        chain_id = int(time.time())
        self.chain_id = chain_id
        self.reset_messages_and_logs()

        while True:
            if loop:
                question = self.output_manager.display_user_input_prompt()
                if question.strip().lower() == 'exit':
                    self.log_and_call_manager.consolidate_logs()    
                    break

            # Check file type to determine path
            file_type = '.db' if hasattr(self, 'conn') else '.csv'
            
            if self.exploratory:
                if file_type == '.db':
                    schema = self.get_db_schema()
                    analyst = 'SQL Analyst'
                    example_code = self.default_example_output_sql
                    plan = self.taskmaster(question, schema)
                else:
                    analyst, plan, query_unknown, query_condition, requires_dataset, confidence = self.taskmaster(
                        question, '' if self.df is None else self.df.columns.tolist()
                    )
                    example_code = self.default_example_output_df if analyst == 'Data Analyst DF' else self.default_example_output_gen
                    
                if not loop and not analyst:
                    self.log_and_call_manager.consolidate_logs()
                    return
                elif not analyst:
                    continue
            else:
                analyst = 'SQL Analyst' if file_type == '.db' else 'Data Analyst DF'
                plan = question
                example_code = self.default_example_output_sql if file_type == '.db' else self.default_example_output_df

            # Generate and execute code
            code = self.generate_code(analyst, question, plan, self.code_messages, example_code)
            
            if file_type == '.db':
                answer, results = self.execute_sql(code, plan, question)
            else:
                answer, results, code = self.execute_code(analyst, code, plan, question, self.code_messages)

            # Display results
            self.output_manager.display_results(
                self.df if file_type == '.csv' else None,
                answer, code, None, False
            )
            
            self.log_and_call_manager.print_summary_to_terminal()
            
            if not loop:
                self.log_and_call_manager.consolidate_logs()
                return 
            
    ######################
    ### Code Functions ###
    ######################
            
    def debug_code(self,analyst,code,question):
        agent = 'Code Debugger'
        # Initialize the messages list with a system message containing the task prompt
        debug_messages = [{"role": "user", "content": self.code_debugger_system.format(code,question)}]
        
        using_model,provider = models.get_model_name(agent)

        self.output_manager.display_tool_start(agent,using_model)

        # Call the OpenAI API
        llm_response = self.llm_stream(self.log_and_call_manager, debug_messages, agent=agent, chain_id=self.chain_id)
        
        # Extract the code from the API response
        debugged_code = self._extract_code(llm_response,analyst,provider)       
        self.output_manager.display_tool_end(agent)

        return debugged_code
    def execute_code(self, analyst, code, plan, original_question, code_messages):
        agent = 'Code Executor'
        # Initialize error correction counter
        error_corrections = 0

        # Create a copy of the original self.df
        if self.df is not None:
            original_df = self.df.copy()

        # Redirect standard output to a StringIO buffer
        with redirect_stdout(io.StringIO()) as output:
            # Try to execute the code and handle errors
            while error_corrections < self.MAX_ERROR_CORRECTIONS:
                try:
                    # Remove the oldest conversation from the messages list
                    self.messages_maintenace(code_messages)

                    # Execute the code
                    if code is not None:
                        local_vars = {'df': self.df} # Create a local variable to store the dataframe
                        exec(code, local_vars) # Execute the code
                        self.df = local_vars['df'] # Update the dataframe with the local variable

                        # Remove examples from the messages list to minimize the number of tokens used
                        code_messages = self._remove_examples(code_messages)
                    break
                except Exception as error:
                    # Capture the full traceback
                    exc_type, exc_value, tb = sys.exc_info()
                    full_traceback = traceback.format_exc()
                    # Filter the traceback
                    exec_traceback = self.filter_exec_traceback(full_traceback, exc_type.__name__, str(exc_value)) 

                    # Increment the error corrections counter
                    error_corrections += 1

                    # Reset df to the original state before trying again
                    if self.df is not None:
                        self.df = original_df.copy()

                    code, code_messages = self.correct_code_errors(exec_traceback, error_corrections, code_messages, analyst)
              
        # Get the output from the executed code
        results = output.getvalue()
        
        # Store the results in a class variable so it can be appended to the subsequent messages list
        self.code_exec_results = results

        summary = self.summarise_solution(original_question, plan, results)

        # Reset the StringIO buffer
        output.truncate(0)
        output.seek(0)

        return summary, results, code

    def generate_code(self, analyst, question, plan, code_messages, example_code):
        """Generate code based on analyst type and input parameters."""
        agent = 'Code Generator'
        using_model, provider = models.get_model_name(agent)
        
        if analyst == 'SQL Analyst':
            schema = self.get_db_schema()
            if hasattr(self, 'code_generator_system_sql'):
                system_message = self.code_generator_system_sql.format(schema=schema)
            else:
                # Fallback to prompt from module if attribute not set
                system_message = prompts.code_generator_system_sql.format(schema=schema)
            
            code_messages[0] = {"role": "system", "content": system_message}
            
            # Similarly handle user message
            if hasattr(self, 'code_generator_user_sql'):
                user_content = self.code_generator_user_sql
            else:
                user_content = prompts.code_generator_user_sql
                
            code_messages.append({
                "role": "user", 
                "content": user_content.format(
                    schema=schema,
                    question=question,
                    results=self.code_exec_results or "No previous results"
                )
            })
            
        # Handle DataFrame analysis path
        else:
            # Set DataFrame system message
            code_messages[0] = {"role": "system", "content": self.code_generator_system_df}
            
            if analyst == 'Data Analyst DF':
                # Prepare DataFrame information
                df_info = (
                    f"{self.df.head(3)}\n\nREQUIRED METRICS AND JOINS:\n{self.query_metrics}" 
                    if self.df_ontology else 
                    self.df.dtypes.to_string(max_rows=None)
                )
                
                # Add user query with DataFrame context
                code_messages.append({
                    "role": "user",
                    "content": self.code_generator_user_df.format(
                        task=question,
                        plan=plan or "No plan provided",
                        df_info=df_info,
                        results=self.code_exec_results or "No previous results",
                        example=example_code
                    )
                })

        # Generate code using LLM
        self.output_manager.display_tool_start(agent, using_model)
        llm_response = self.llm_stream(
            self.log_and_call_manager,
            code_messages,
            agent=agent,
            chain_id=self.chain_id
        )
        
        # Add response to message history
        code_messages.append({"role": "assistant", "content": llm_response})
        
        # Extract appropriate code from response
        if analyst == 'SQL Analyst':
            code = self._extract_sql_query(llm_response)
        else:
            code = self._extract_code(llm_response, analyst, provider)
            
        if self.debug:
            print(f"Generated Code: {code}")
            
        return code
    
    def filter_exec_traceback(self, full_traceback, exception_type, exception_value):
        # Split the full traceback into lines and filter those that originate from "<string>"
        filtered_tb_lines = [line for line in full_traceback.split('\n') if '<string>' in line]

        # Combine the filtered lines and append the exception type and message
        filtered_traceback = '\n'.join(filtered_tb_lines)
        if filtered_traceback:  # Add a newline only if there's a traceback to show
            filtered_traceback += '\n'
        filtered_traceback += f"{exception_type}: {exception_value}"

        return filtered_traceback
    
    def correct_code_errors(self, error, error_corrections, code_messages, analyst):
        agent = 'Error Corrector'

        model,provider = models.get_model_name(agent)

        #If error correction is greater than 2 remove the first error correction
        if error_corrections > 2:
            del code_messages[-4] 
            del code_messages[-3]
        
        # Append the error message to the messages list
        code_messages.append({"role": "user", "content": self.error_corector_system.format(error)})

        # Display the error message
        self.output_manager.display_error(error)

        llm_response = self.llm_call(self.log_and_call_manager,code_messages,agent=agent, chain_id=self.chain_id)
        code_messages.append({"role": "assistant", "content": llm_response})
        code = self._extract_code(llm_response,analyst,provider)

        return code, code_messages

    def rank_code(self,results, code, question):
        agent = 'Code Ranker'
        # Initialize the messages list with a user message containing the task prompt
        rank_messages = [{"role": "user", "content": self.code_ranker_system.format(code,results,question)}]

        using_model,provider = models.get_model_name(agent)

        self.output_manager.display_tool_start(agent,using_model)

        # Call the OpenAI API 
        llm_response = self.llm_call(self.log_and_call_manager,rank_messages,agent=agent, chain_id=self.chain_id)

        # Extract the rank from the API response
        rank = self._extract_rank(llm_response)       

        return rank
    
    ############################
    ## Summarise the solution ##
    ############################

    def summarise_solution(self, original_question, plan, results):
        agent = 'Solution Summarizer'

        # Initialize the messages list with a user message containing the task prompt
        insights_messages = [{"role": "user", "content": self.solution_summarizer_system.format(original_question, plan, results)}]
        # Call the OpenAI API
        summary = self.llm_call(self.log_and_call_manager,insights_messages,agent=agent, chain_id=self.chain_id)

        return summary
    def handle_sql_database(self, db_path):
        """Initialize SQL connection and extract schema"""
        import sqlite3
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()
        
    def execute_sql(self, query: str, plan: str, question: str):
        """Execute SQL queries and format results with proper schema handling.
        
        Args:
            query (str): SQL query to be executed
            plan (str): Task plan or context
            question (str): Original user question
            
        Returns:
            tuple: A summary of results and the executed query
        """
        try:
            if not query:
                return None, "No valid SQL query provided."
            
            results = []
            # Split and clean queries (ignore comments and empty lines)
            queries = [q.strip() for q in query.split(';') if q.strip()]
            
            for q in queries:
                try:
                    # Execute query
                    self.cur.execute(q)
                    result = self.cur.fetchall()
                    
                    if "pragma" in q.lower():
                        # Format PRAGMA schema results
                        columns = [desc[0] for desc in self.cur.description]
                        df = pd.DataFrame(result, columns=columns)
                        results.append(f"\nSchema for {q.split('(')[-1].split(')')[0]} table:\n{df.to_string()}")
                    elif result:
                        # Format normal query results
                        columns = [desc[0] for desc in self.cur.description]
                        df = pd.DataFrame(result, columns=columns)
                        results.append(f"\nResults for query: {q}\n{df.to_string()}")
                    else:
                        results.append(f"Query executed successfully but returned no results: {q}")
                except Exception as e:
                    results.append(f"Error executing query: {q}\n{str(e)}")
            
            # Combine all results
            summary = "\n".join(results)
            return summary, query

        except Exception as e:
            self.output_manager.display_error(f"SQL Execution Error: {str(e)}")
            return None, None


    def get_db_schema(self):
        """Extract and format database schema."""
        try:
            # Get list of tables
            self.cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = self.cur.fetchall()
            
            schema = []
            for table in tables:
                table_name = table[0]
                self.cur.execute(f"PRAGMA table_info({table_name});")
                columns = self.cur.fetchall()
                
                table_schema = [f"Table: {table_name}"]
                table_schema.extend([f"  - {col[1]} ({col[2]})" for col in columns])
                schema.append("\n".join(table_schema))
                
            return "\n\n".join(schema)
        except Exception as e:
            print(f"Error getting schema: {str(e)}")
            return None