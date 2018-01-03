import json
import os
import lib.community

headers = { "Content-type": "application/json", "Access-Control-Allow-Origin": "*" }

def get_user_profile(event, context):
    user = event['requestContext']['authorizer']['principalId']

    profile = { "activities" : get_profile(user) }

    return {
        "statusCode": 200,
        "body": json.dumps(profile),
        "headers": headers
    }

def get_user_activities(event, context):
    user = event['requestContext']['authorizer']['principalId']
    limit = event['queryStringParameters'].get('limit')

    activities = { "activities" : get_activities(user, limit) }

    return {
        "statusCode": 200,
        "body": json.dumps(activities),
        "headers": headers
    }

def create_user(event, context):
    auth =  event['requestContext']['authorizer']
    user =  auth['principalId']
    email = auth['email']
    name =  auth['name']

    result = create(user, name, email)

    return {
        "statusCode": 200,
        "body": json.dumps(result),
        "headers": headers
    }

def update_personal(event, context):
    body = event['body']
    auth =  event['requestContext']['authorizer']
    user =  auth['principalId']
    name =  auth['name']

    result = update_personal(user, name , body.get('bio'), body.get('image'), body.get('dob')): 

    return {
        "statusCode": 200,
        "body": json.dumps(result),
        "headers": headers
    }

def update_company(event, context):
    body = event['body']
    auth =  event['requestContext']['authorizer']
    user =  auth['principalId']
    name =  auth['name']

    result = update_personal(user, name , body.get('bio'), body.get('image'), body.get('dob')): 

    return {
        "statusCode": 200,
        "body": json.dumps(result),
        "headers": headers
    }
