'''
Test cases for Talk2Biomodels.
'''

import pandas as pd
from langchain_core.messages import HumanMessage, ToolMessage
from ..agents.t2b_agent import get_app

def test_get_modelinfo_tool():
    '''
    Test the get_modelinfo tool.
    '''
    unique_id = 12345
    app = get_app(unique_id)
    config = {"configurable": {"thread_id": unique_id}}
    # Update state
    app.update_state(config,
      {"sbml_file_path": ["aiagents4pharma/talk2biomodels/tests/BIOMD0000000449_url.xml"]})
    prompt = "Extract all relevant information from the uploaded model."
    # Test the tool get_modelinfo
    response = app.invoke(
                        {"messages": [HumanMessage(content=prompt)]},
                        config=config
                    )
    assistant_msg = response["messages"][-1].content
    # Check if the assistant message is a string
    assert isinstance(assistant_msg, str)

def test_search_models_tool():
    '''
    Test the search_models tool.
    '''
    unique_id = 12345
    app = get_app(unique_id)
    config = {"configurable": {"thread_id": unique_id}}
    # Update state
    app.update_state(config, {"llm_model": "gpt-4o-mini"})
    prompt = "Search for models on Crohn's disease."
    # Test the tool get_modelinfo
    response = app.invoke(
                        {"messages": [HumanMessage(content=prompt)]},
                        config=config
                    )
    assistant_msg = response["messages"][-1].content
    # Check if the assistant message is a string
    assert isinstance(assistant_msg, str)
    # Check if the assistant message contains the
    # biomodel id BIO0000000537
    assert "BIOMD0000000537" in assistant_msg

def test_ask_question_tool():
    '''
    Test the ask_question tool without the simulation results.
    '''
    unique_id = 12345
    app = get_app(unique_id, llm_model='gpt-4o-mini')
    config = {"configurable": {"thread_id": unique_id}}

    ##########################################
    # Test ask_question tool when simulation
    # results are not available i.e. the
    # simulation has not been run. In this
    # case, the tool should return an error
    ##########################################
    # Update state
    app.update_state(config, {"llm_model": "gpt-4o-mini"})
    # Define the prompt
    prompt = "Call the ask_question tool to answer the "
    prompt += "question: What is the concentration of CRP "
    prompt += "in serum at 1000 hours? The simulation name "
    prompt += "is `simulation_name`."
    # Invoke the tool
    app.invoke(
            {"messages": [HumanMessage(content=prompt)]},
            config=config
        )
    # Get the messages from the current state
    # and reverse the order
    current_state = app.get_state(config)
    reversed_messages = current_state.values["messages"][::-1]
    # Loop through the reversed messages until a
    # ToolMessage is found.
    for msg in reversed_messages:
        # Assert that the message is a ToolMessage
        # and its status is "error"
        if isinstance(msg, ToolMessage):
            assert msg.status == "error"

def test_simulate_model_tool():
    '''
    Test the simulate_model tool when simulating
    multiple models.
    '''
    unique_id = 123
    app = get_app(unique_id)
    config = {"configurable": {"thread_id": unique_id}}
    app.update_state(config, {"llm_model": "gpt-4o-mini"})
    # Upload a model to the state
    app.update_state(config,
        {"sbml_file_path": ["aiagents4pharma/talk2biomodels/tests/BIOMD0000000449_url.xml"]})
    prompt = "Simulate models 64 and the uploaded model"
    # Invoke the agent
    app.invoke(
        {"messages": [HumanMessage(content=prompt)]},
        config=config
    )
    current_state = app.get_state(config)
    dic_simulated_data = current_state.values["dic_simulated_data"]
    # Check if the dic_simulated_data is a list
    assert isinstance(dic_simulated_data, list)
    # Check if the length of the dic_simulated_data is 2
    assert len(dic_simulated_data) == 2
    # Check if the source of the first model is 64
    assert dic_simulated_data[0]['source'] == 64
    # Check if the source of the second model is upload
    assert dic_simulated_data[1]['source'] == "upload"
    # Check if the data of the first model contains
    assert '1,3-bisphosphoglycerate' in dic_simulated_data[0]['data']
    # Check if the data of the second model contains
    assert 'mTORC2' in dic_simulated_data[1]['data']

def test_integration():
    '''
    Test the integration of the tools.
    '''
    unique_id = 123
    app = get_app(unique_id)
    config = {"configurable": {"thread_id": unique_id}}
    app.update_state(config, {"llm_model": "gpt-4o-mini"})
    # ##########################################
    # ## Test simulate_model tool
    # ##########################################
    prompt = "Simulate the model 537 for 2016 hours and intervals"
    prompt += " 2016 with an initial concentration of `DoseQ2W` "
    prompt += "set to 300 and `Dose` set to 0. Reset the concentration"
    prompt += " of `NAD` to 100 every 500 hours."
    # Test the tool get_modelinfo
    response = app.invoke(
                        {"messages": [HumanMessage(content=prompt)]},
                        config=config
                    )
    assistant_msg = response["messages"][-1].content
    print (assistant_msg)
    # Check if the assistant message is a string
    assert isinstance(assistant_msg, str)
    ##########################################
    # Test ask_question tool when simulation
    # results are available
    ##########################################
    # Update state
    app.update_state(config, {"llm_model": "gpt-4o-mini"})
    prompt = "What is the concentration of CRP in serum at 1000 hours? "
    # prompt += "Show only the concentration, rounded to 1 decimal place."
    # prompt += "For example, if the concentration is 0.123456, "
    # prompt += "your response should be `0.1`. Do not return any other information."
    # Test the tool get_modelinfo
    response = app.invoke(
                        {"messages": [HumanMessage(content=prompt)]},
                        config=config
                    )
    assistant_msg = response["messages"][-1].content
    # print (assistant_msg)
    # Check if the assistant message is a string
    assert "1.7" in assistant_msg

    ##########################################
    # Test custom_plotter tool when the
    # simulation results are available
    ##########################################
    prompt = "Plot only CRP related species."

    # Update state
    app.update_state(config, {"llm_model": "gpt-4o-mini"}
                    )
    # Test the tool get_modelinfo
    response = app.invoke(
                        {"messages": [HumanMessage(content=prompt)]},
                        config=config
                    )
    assistant_msg = response["messages"][-1].content
    current_state = app.get_state(config)
    # Get the messages from the current state
    # and reverse the order
    reversed_messages = current_state.values["messages"][::-1]
    # Loop through the reversed messages
    # until a ToolMessage is found.
    expected_header = ['Time', 'CRP[serum]', 'CRPExtracellular']
    expected_header += ['CRP Suppression (%)', 'CRP (% of baseline)']
    expected_header += ['CRP[liver]']
    predicted_artifact = []
    for msg in reversed_messages:
        if isinstance(msg, ToolMessage):
            # Work on the message if it is a ToolMessage
            # These may contain additional visuals that
            # need to be displayed to the user.
            if msg.name == "custom_plotter":
                predicted_artifact = msg.artifact
                break
    # Convert the artifact into a pandas dataframe
    # for easy comparison
    df = pd.DataFrame(predicted_artifact)
    # Extract the headers from the dataframe
    predicted_header = df.columns.tolist()
    # Check if the header is in the expected_header
    # assert expected_header in predicted_artifact
    assert set(expected_header).issubset(set(predicted_header))
    ##########################################
    # Test custom_plotter tool when the
    # simulation results are available but
    # the species is not available
    ##########################################
    prompt = "Plot the species `TP53`."

    # Update state
    app.update_state(config, {"llm_model": "gpt-4o-mini"}
                    )
    # Test the tool get_modelinfo
    response = app.invoke(
                        {"messages": [HumanMessage(content=prompt)]},
                        config=config
                    )
    assistant_msg = response["messages"][-1].content
    # print (response["messages"])
    current_state = app.get_state(config)
    # Get the messages from the current state
    # and reverse the order
    reversed_messages = current_state.values["messages"][::-1]
    # Loop through the reversed messages until a
    # ToolMessage is found.
    predicted_artifact = []
    for msg in reversed_messages:
        if isinstance(msg, ToolMessage):
            # Work on the message if it is a ToolMessage
            # These may contain additional visuals that
            # need to be displayed to the user.
            if msg.name == "custom_plotter":
                predicted_artifact = msg.artifact
                break
    # Check if the the predicted artifact is `None`
    assert predicted_artifact is None
