"""
Google Calendar Service for ACNSMS
Handles Google Calendar integration
"""

import os
import pickle
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()

class CalendarService:
    """Service class for Google Calendar integration"""
    
    # Google Calendar API scopes
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self):
        self.service = None
        self.calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')
        self.credentials_file = 'credentials.json'
        self.token_file = 'token.pickle'
        
        # Initialize Google Calendar service
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        
        # Check if token file exists
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Failed to refresh credentials: {str(e)}")
                    creds = None
            
            if not creds:
                if os.path.exists(self.credentials_file):
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_file, self.SCOPES)
                        creds = flow.run_local_server(port=0)
                    except Exception as e:
                        print(f"Failed to authenticate: {str(e)}")
                        return
                else:
                    print("Google Calendar credentials file not found")
                    return
            
            # Save credentials for future use
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        try:
            self.service = build('calendar', 'v3', credentials=creds)
            print("Google Calendar service initialized successfully")
        except Exception as e:
            print(f"Failed to build Google Calendar service: {str(e)}")
    
    def create_event(self, title, location, start_datetime, end_datetime, description=""):
        """
        Create a new calendar event
        
        Args:
            title (str): Event title
            location (str): Event location
            start_datetime (datetime): Event start date and time
            end_datetime (datetime): Event end date and time
            description (str): Event description
        
        Returns:
            str: Event ID if successful, None otherwise
        """
        if not self.service:
            print("Google Calendar service not available")
            return None
        
        try:
            event = {
                'summary': title,
                'location': location,
                'description': description,
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'UTC',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 24 hours before
                        {'method': 'popup', 'minutes': 30},       # 30 minutes before
                    ],
                },
            }
            
            event_result = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            print(f"Event created successfully: {event_result['id']}")
            return event_result['id']
            
        except HttpError as error:
            print(f"An error occurred while creating event: {error}")
            return None
        except Exception as e:
            print(f"Failed to create calendar event: {str(e)}")
            return None
    
    def update_event(self, event_id, title=None, location=None, start_datetime=None, end_datetime=None, description=None):
        """
        Update an existing calendar event
        
        Args:
            event_id (str): Event ID to update
            title (str): New event title
            location (str): New event location
            start_datetime (datetime): New event start date and time
            end_datetime (datetime): New event end date and time
            description (str): New event description
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.service:
            print("Google Calendar service not available")
            return False
        
        try:
            # Get the existing event
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            # Update only provided fields
            if title:
                event['summary'] = title
            if location:
                event['location'] = location
            if description:
                event['description'] = description
            if start_datetime:
                event['start'] = {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'UTC',
                }
            if end_datetime:
                event['end'] = {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'UTC',
                }
            
            # Update the event
            updated_event = self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            print(f"Event updated successfully: {updated_event['id']}")
            return True
            
        except HttpError as error:
            print(f"An error occurred while updating event: {error}")
            return False
        except Exception as e:
            print(f"Failed to update calendar event: {str(e)}")
            return False
    
    def delete_event(self, event_id):
        """
        Delete a calendar event
        
        Args:
            event_id (str): Event ID to delete
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.service:
            print("Google Calendar service not available")
            return False
        
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            print(f"Event deleted successfully: {event_id}")
            return True
            
        except HttpError as error:
            print(f"An error occurred while deleting event: {error}")
            return False
        except Exception as e:
            print(f"Failed to delete calendar event: {str(e)}")
            return False
    
    def get_events(self, start_date=None, end_date=None, max_results=10):
        """
        Get calendar events within a date range
        
        Args:
            start_date (datetime): Start date for event search
            end_date (datetime): End date for event search
            max_results (int): Maximum number of events to return
        
        Returns:
            list: List of events
        """
        if not self.service:
            print("Google Calendar service not available")
            return []
        
        try:
            # Default to current time if no start date provided
            if not start_date:
                start_date = datetime.utcnow()
            
            # Default to one month from start date if no end date provided
            if not end_date:
                end_date = start_date + timedelta(days=30)
            
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=start_date.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return events
            
        except HttpError as error:
            print(f"An error occurred while getting events: {error}")
            return []
        except Exception as e:
            print(f"Failed to get calendar events: {str(e)}")
            return []