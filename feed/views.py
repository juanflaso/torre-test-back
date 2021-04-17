from django.shortcuts import render
from rest_framework.decorators import api_view
from django.http import HttpResponse
from .constants import TORRE_OPPORTUNITIES_SEARCH_URL, GOOD_OPPS_SHOWN_AT_START, NOT_GOOD_OPPS_SHOWN_AT_ALTERNATING_START, GOOD_OPPS_SHOWN_ALTERNATING
from .QueryParser import QueryParser
import requests
import json
# Create your views here.

queryParser = QueryParser()

@api_view(['POST'])
def getFeed(request):
    request_data = request.data

    query = request_data['query']

    parsedText = queryParser.getPairings(query)

    query = { "and": parsedText}

    headers = {'Content-type': 'application/json'}
    response = requests.post(TORRE_OPPORTUNITIES_SEARCH_URL, data = json.dumps(query), headers=headers).json()

    results = response["results"]

    if len(response["results"]) > 0:
        indexesOfResultsReordered = getListOfAlternatingIndexes(len(results))

        mixedAlternatingResponse = generateMixedAlternatingResponse(results, indexesOfResultsReordered)

        return HttpResponse(json.dumps(mixedAlternatingResponse), content_type='application/json')
    
    errorDictionary = [{"type": "error", "result": "No results for your search!"}]

    return HttpResponse(json.dumps(errorDictionary), content_type='application/json')


def generateMixedAlternatingResponse(results, indexesOfResultsReordered):

    mixedAlternatingResponse = []
    peopleList = []
    organizationsList = []

    showPeople = True

    lastIndex = 0
    for index in indexesOfResultsReordered:

        # If the difference between the current index and last index is more than 1,
        # that means that we are showing a not so good opportunity next. 
        # So, let's use this space to "keep the user on his toes" and show him another kind of thing
        # like people or organizations to signal
        if index - lastIndex > 1:
            if showPeople:
                mixedAlternatingResponse.append(
                    {
                        "type": "people",
                        "result": list({v['subjectId']:v for v in peopleList}.values())
                    }
                )

                peopleList = []
                showPeople = False

            else:
                mixedAlternatingResponse.append(
                    {
                        "type": "organization",
                        "result": list({v['id']:v for v in organizationsList}.values()) #unique values
                    }
                )

                organizationsList = []
                showPeople = True

        # Add organizations and people to their respective lists
        organizationsList.extend(getOrganizationFromOpportunity(results[index]))
        peopleList.extend(results[index]["members"])
        
        # Add the opportunity to the list
        mixedAlternatingResponse.append(
            {
                "type": "opportunity",
                "result": results[index]
            }
        )

        lastIndex = index
    
    return mixedAlternatingResponse


def getOrganizationFromOpportunity(opportunity):
    organizationsList = opportunity["organizations"]

    resultOrganizationList = []
    if not organizationsList:
        return resultOrganizationList

    for organization in organizationsList:
        resultOrganizationList.append(
            {
                "id": organization["id"],
                "name": organization["name"],
                "picture": organization["picture"],
                "members": opportunity["members"]
                
            }
        )

    return resultOrganizationList



def getListOfAlternatingIndexes(responseSize):

    #If the response has 6 or less items, then the result will be almost the same list, so return the same
    if responseSize <= 6: 
        return list(range(0,7))
    
    responseWithoutStart = responseSize - GOOD_OPPS_SHOWN_AT_START #Always show first the 3 best results

    #We start showing 2 not so good opps and 1 good opp, so 3.
    alternatingOppsShown = NOT_GOOD_OPPS_SHOWN_AT_ALTERNATING_START + GOOD_OPPS_SHOWN_ALTERNATING 

    offsetCount = 0
    while responseWithoutStart > 0:

        responseWithoutStart -= alternatingOppsShown

        offsetCount += 1
        alternatingOppsShown += 1 # increase the number of not so good opps shown on each step.

    
    listOfAlternatingIndexes = [0,1,2]

    notSoGoodResultsRange = NOT_GOOD_OPPS_SHOWN_AT_ALTERNATING_START
    notSoGoodResultsOffset = (GOOD_OPPS_SHOWN_AT_START - 1) + offsetCount # -1 to translate to index
    goodResultsOffset = GOOD_OPPS_SHOWN_AT_START
    while len(listOfAlternatingIndexes) < responseSize:

        listOfAlternatingIndexes.extend(list(range(notSoGoodResultsOffset, notSoGoodResultsOffset + notSoGoodResultsRange)))
        listOfAlternatingIndexes.append(goodResultsOffset)

        notSoGoodResultsOffset += notSoGoodResultsRange
        goodResultsOffset += 1
        notSoGoodResultsRange += 1

    return listOfAlternatingIndexes[:responseSize]
