import datetime
import requests
import os.path
import pandas as pd
import yfinance as yf
import concurrent.futures

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from langchain.tools import tool
from langchain_core.utils.function_calling import convert_to_openai_function, convert_to_openai_tool
from typing import List, Callable
from langchain_core.tools import BaseTool
import inspect
import sys
# #If modifying these scopes, delete the file token.json.
# SCOPES = ["https://www.googleapis.com/auth/calendar"]

# """Shows basic usage of the Google Calendar API.
# Prints the start and name of the next 10 events on the user's calendar.
# """
# creds = None
# # The file token.json stores the user's access and refresh tokens, and is
# # created automatically when the authorization flow completes for the first
# # time.
# if os.path.exists("token.json"):
#   creds = Credentials.from_authorized_user_file("token.json", SCOPES)
# # If there are no (valid) credentials available, let the user log in.
# if not creds or not creds.valid:
#   if creds and creds.expired and creds.refresh_token:
#     creds.refresh(Request())
#   else:
#     flow = InstalledAppFlow.from_client_secrets_file(
#         r"C:\Users\PC\Desktop\program\fine tune\calendar config\localtestconf.json", SCOPES
#     )
#     creds = flow.run_local_server(host="localhost", port=3000, open_browser=True)
#   # Save the credentials for the next run
#   with open("token.json", "w") as token:
#     token.write(creds.to_json())

@tool
def get_calendarlist()->str:
  """
  This function is to get the calendarlist in the google calendar that user signed in,
  map available calendar name with calendar id.

  Return:
    calendarList = "calendarsummary": "calendarid"
    example:
      calendarList = {'Holidays in Malaysia': 'en.malaysia.official#holiday@group.v.calendar.google.com', 
                      'test': '13b5e0426546e87c0bc04dc502acd2b556f0a9c687c680e32f37c82f76ccbd0f@group.calendar.google.com'}
  """
  service = build("calendar", "v3", credentials=creds)
  calendar_list = service.calendarList().list().execute()

  calendarList = {item['summary']:item['id']  for item in calendar_list.get('items', [])}
  return calendarList

@tool
def get_event(calendar_id:str, time_min:str, max_results:int=10, order_by:str="startTime")->str:
  """
  Retrieves upcoming events from a specific Google Calendar.

  Args:
    calendar_id (str): the ID of the calendar to retrieve events from.
            Example: "primary", "your-email@gmail.com", "abc123@group.calendar.google.com"
    time_min (str): The lower bound (RFC3339 timestamp) for an event’s start time to filter from.
            Example: datetime.datetime.utcnow().isoformat() + 'Z, (e.g: "2025-07-11T00:00:00")
    max_results (str): The maximum number of events to retrieve. Default is 10.
    order_by (str): The order in which to return results. Default is "startTime".
            Other valid option: "updated"

  Returns:
    str: A formatted list of upcoming events. if no events are found, returns a message indicating that.
  
  Example:
    get_event(calendar_id="primary", time_min"2025-07-11T00:00:00Z", max_results=10)
  """
  try:
    service = build("calendar", "v3", credentials=creds)
    # Call the Calendar API
    time_min= datetime.datetime.now(tz=datetime.timezone.utc).isoformat()

    print("Getting the upcoming 10 events")

    events_result = (service.events().list(
      calendarId= calendar_id,
      timeMin=time_min, 
      maxResults=max_results, 
      singleEvents=True, 
      orderBy=order_by
      ).execute()
    )
    events = events_result.get("items", [])
    if not events:
      print("No upcoming events found.")
      return
    # Prints the start and name of the next 10 events
    result = []
    for event in events:
     
      start = event["start"].get("dateTime", event["start"].get("date"))
      end = event['end'].get("dateTime", event['end'].get("date"))
      summary = event.get("summary", "No Title")
      eventid = event.get('id')
      eventlink = event.get('htmlLink')
      body ={
         "Title": summary,
         "start_datetime": start,
         "end_datetime": end,
         "event_ID": eventid,
         "eventlink": eventlink
      }
      result.append(body)
    return (result)
  
  except HttpError as error:
    print(f"An error occurred: {error}")

@tool
def create_event(calendar_id: str, summary: str, description: str, start_time: str, end_time: str, timezone: str = "Asia/Kuala_Lumpur"):
    """
    Creates a calendar event.

    Args:
        calendar_id (str): The ID of the calendar where the event should be created. Example: 'primary'
        summary (str): Title of the event.
        description (str): Description of the event.
        start_time (str): Start datetime in ISO 8601 format (e.g. "2025-07-12T09:00:00").
        end_time (str): End datetime in ISO 8601 format (e.g. "2025-07-12T10:00:00").
        timezone (str): Timezone for the event. Default is "Asia/Kuala_Lumpur".

    Returns:
        str: The link to the created event, or an error message.
    """
    try:
        service = build("calendar", "v3", credentials=creds)

        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_time,
                'timeZone': timezone,
            },
        }

        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()

        print(f"Event created: {created_event.get('htmlLink')}")
        return created_event.get('htmlLink')

    except HttpError as error:
        return f"An error occurred: {error}"

@tool
def update_event(calendar_id: str, event_id: str, new_summary: str = None, new_description: str = None, new_start: str = None, new_end: str = None):
    """
    Updates an existing event in the specified calendar.

    Args:
        calendar_id (str): Calendar ID where the event exists.
        event_id (str): The ID of the event to update.
        new_summary (str): New title (optional).
        new_description (str): New description (optional).
        new_start (str): New start time in ISO format (optional) (e.g.: "2025-07-29T08:00:00").
        new_end (str): New end time in ISO format (optional) (e.g.: "2025-07-29T08:00:00").
    """
    try:
        service = build("calendar", "v3", credentials=creds)
        
        # Get existing event
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()

        # Update fields only if new values are provided
        if new_summary:
            event['summary'] = new_summary
        if new_description:
            event['description'] = new_description
        if new_start:
            event['start']['dateTime'] = new_start
        if new_end:
            event['end']['dateTime'] = new_end

        # Update event
        updated_event = service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()

        print(f"Event updated: {updated_event.get('htmlLink')}")
        return updated_event.get('htmlLink')

    except HttpError as error:
        print(f"An error occurred while updating: {error}")

@tool
def delete_event(calendar_id: str, event_id: str):
    """
    Deletes an event from the specified calendar.

    Args:
        calendar_id (str): Calendar ID.
        event_id (str): Event ID to delete.
    """
    try:
        service = build("calendar", "v3", credentials=creds)
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        print(f"Event {event_id} deleted successfully.\n")
    except HttpError as error:
        print(f"An error occurred while deleting: {error}")

@tool
def get_event_by_id(calendar_id: str, event_id: str):
    """
    Retrieves a single event from a Google Calendar using its event ID.

    Args:
        calendar_id (str): The calendar ID containing the event. Example: 'primary'.
        event_id (str): The unique ID of the event to retrieve.

    Returns:
        dict: The full event object if found.
    """
    try:
        service = build("calendar", "v3", credentials=creds)
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        
        # Print key event details
        print(f"Title: {event.get('summary')}")
        print(f"Start: {event['start'].get('dateTime', event['start'].get('date'))}")
        print(f"End: {event['end'].get('dateTime', event['end'].get('date'))}")
        print(f"Description: {event.get('description', 'No description')}")
        
        return event

    except HttpError as error:
        print(f"An error occurred while retrieving the event: {error}")
        return None

@tool
def get_current_stock_price(symbol: str) -> float:
  """
  Get the current stock price for a given symbol.

  Args:
    symbol (str): The stock symbol.

  Returns:
    float: The current stock price, or None if an error occurs.
  """
  try:
    stock = yf.Ticker(symbol)
    # Use "regularMarketPrice" for regular market hours, or "currentPrice" for pre/post market
    current_price = stock.info.get("regularMarketPrice", stock.info.get("currentPrice"))
    return current_price if current_price else None
  except Exception as e:
    print(f"Error fetching current price for {symbol}: {e}")
    return None    

@tool
def get_stock_fundamentals(symbol: str) -> dict:
    """
    Get fundamental data for a given stock symbol using yfinance API.

    Args:
        symbol (str): The stock symbol.

    Returns:
        dict: A dictionary containing fundamental data.
            Keys:
                - 'symbol': The stock symbol.
                - 'company_name': The long name of the company.
                - 'sector': The sector to which the company belongs.
                - 'industry': The industry to which the company belongs.
                - 'market_cap': The market capitalization of the company.
                - 'pe_ratio': The forward price-to-earnings ratio.
                - 'pb_ratio': The price-to-book ratio.
                - 'dividend_yield': The dividend yield.
                - 'eps': The trailing earnings per share.
                - 'beta': The beta value of the stock.
                - '52_week_high': The 52-week high price of the stock.
                - '52_week_low': The 52-week low price of the stock.
    """
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        fundamentals = {
            'symbol': symbol,
            'company_name': info.get('longName', ''),
            'sector': info.get('sector', ''),
            'industry': info.get('industry', ''),
            'market_cap': info.get('marketCap', None),
            'pe_ratio': info.get('forwardPE', None),
            'pb_ratio': info.get('priceToBook', None),
            'dividend_yield': info.get('dividendYield', None),
            'eps': info.get('trailingEps', None),
            'beta': info.get('beta', None),
            '52_week_high': info.get('fiftyTwoWeekHigh', None),
            '52_week_low': info.get('fiftyTwoWeekLow', None)
        }
        return fundamentals
    except Exception as e:
        print(f"Error getting fundamentals for {symbol}: {e}")
        return {}

@tool
def get_company_news(symbol: str) -> pd.DataFrame:
    """
    Get company news and press releases for a given stock symbol.

    Args:
    symbol (str): The stock symbol.

    Returns:
    pd.DataFrame: DataFrame containing company news and press releases.
    """
    try:
        news = yf.Ticker(symbol).news
        return news
    except Exception as e:
        print(f"Error fetching company news for {symbol}: {e}")
        return pd.DataFrame()

@tool
def get_company_profile(symbol: str) -> dict:
    """
    Get company profile and overview for a given stock symbol.

    Args:
    symbol (str): The stock symbol.

    Returns:
    dict: Dictionary containing company profile and overview.
    """
    try:
        profile = yf.Ticker(symbol).info
        return profile
    except Exception as e:
        print(f"Error fetching company profile for {symbol}: {e}")
        return {}

def get_openai_tools()->List[dict]:
   function = [
      create_event,
      get_event,
      update_event,
      delete_event,
      get_event_by_id,
      get_calendarlist,
      get_current_stock_price,
      get_stock_fundamentals,
      get_company_news,
      get_company_profile
   ]

   tools = [convert_to_openai_function(f) for f in function]
   return tools



# import json
# #print(json.dumps(available_functions, indent=2))

# from langchain.agents import initialize_agent, AgentType
# from langchain_ollama import ChatOllama
# import ollama
# from langchain.agents import AgentExecutor, create_react_agent
# from langchain_core.prompts import ChatPromptTemplate


# template = '''
# Answer the following questions as best you can. You have access to the following tools:

# {tools}

# Use the following format strictly:

# Question: the input question you must answer
# Thought: you should always think about what to do
# Action: the action to take, should be one of [{tool_names}]
# Action Input: the input to the action
# Observation: the result of the action
# ... (this Thought/Action/Action Input/Observation can repeat N times)
# Thought: I now know the final answer
# Final Answer: the final answer to the original input question

# Begin!

# Question: {input}
# Thought:{agent_scratchpad}
# '''

# current_module = sys.modules[__name__]
# tools = [
#    obj for name, obj in inspect.getmembers(current_module)
#    if isinstance(obj, BaseTool)
# ]

# model= ChatOllama(model="llama3.2")
# prompt = ChatPromptTemplate.from_template(template)
# agent = create_react_agent(model, tools, prompt)
# agent_executor=AgentExecutor(agent=agent, tools=tools , verbose=True, handle_parsing_errors=True)

# agent_executor.invoke({ 
#    "input": "can you read any available event on 7/july/2025?"
# })

