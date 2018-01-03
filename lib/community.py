import os

from neo4j.v1 import GraphDatabase, basic_auth
from encryption import decrypt_value_str

neo4j_url = 'bolt://%s' % (decrypt_value_str(os.environ['COMMUNITY_GRAPH_DB_HOST_PORT']))
neo4j_user = decrypt_value_str(os.environ['COMMUNITY_GRAPH_DB_USER']) 
neo4j_password = decrypt_value_str(os.environ['COMMUNITY_GRAPH_DB_PW'])

db_driver = GraphDatabase.driver(neo4j_url,  auth=basic_auth(neo4j_user, neo4j_password))

def sanitize(str):
    str.replace('<', '&lt;').replace('>', '&gt;')

def remove_none(dict):
	{key: value for key, value in dict.items() if value is not None}

def create(userId, userName, userEmail): 
  session = db_driver.session()
  query = """
    CREATE (p:Person {id:{id}})
    SET p.name = {userName},p.email = {userEmail}
    """
  results = session.run(query, parameters={"id": userId, "userName": userName, "userEmail": userEmail})
  results.consume()

def update_personal(userId, userName, userBio, userImage, dob): 
  session = db_driver.session()
  query = """
    MATCH (p:Person {id:{id}})
    SET p += {data}
    """
  results = session.run(query, parameters={"id": userId, "data": {"name": userName, "bio": userBio, "image": userImage, "dob": dob}})
  results.consume()

def update_address(userId, country, state, city, zip, street): 
  session = db_driver.session()
  query = """
    MATCH (p:Person {id:{id}})
    SET p += {data}
    """
  results = session.run(query, parameters={"id": userId, "data": {"country":country, "street":street, "state":state, "city":city, "zip":zip}})
  results.consume()

def update_company(userId, company, title, since): 
  session = db_driver.session()
  query = """
    MATCH (p:Person {id:{id}})
    MERGE (c:Company {name:{company}})
    MERGE (p)-[r:WORKED_AT]->(c) SET r.title = {title}, r.since = {since}
    """
  results = session.run(query, parameters={"id": userId, "company":company, "title":title, "since":since})
  results.consume()

def add_badge(userId, badge, time, score): 
  session = db_driver.session()
  query = """
    MATCH (p:Person {id:{id}})
    MATCH (b:Badge {badge:{badge}})
    MERGE (p)-[r:ACHIEVED]->(b) SET r.created = coalesce({time},timestamp()/1000), r.score = {score}
    """
  results = session.run(query, parameters={"id": userId, "badge":badge, "score":score, "time":time})
  results.consume()

accounts = {"google":"Google","meetup":"Meetup","github":"GitHub","stackoverflow","StackOverflow","slack":"Slack","linkedin":"LinkedIn","facebook":"Facebook","twitter":"Twitter"}

def add_account(userId, accountId, type, link=None, email=None): 
  account = accounts[type.lower()]
  if account is None:
	raise Exception("No such account "+type)
  data = {}
  if link is not None : data["link"] = link
  if email is not None : data["email"] = email
  id = "id"
  if account == "Twitter" : id = "screen_name"
  if account == "GitHub" : id = "name" 
  # slack email or id

  session = db_driver.session()
  query = """
    MATCH (p:Person {{id:$id}})
    MERGE (a:User:`{label}` {{`{id}`:$accountId}}) SET a+= $data
    MERGE (p)-[r:REGISTERED]->(a) SET r.time = timestamp()
    """.format(label=account)
  results = session.run(query, parameters={"id": userId, "accountId":accountId,"data":data})
  results.consume()

def add_twitter_contributions(): 
  session = db_driver.session()
  query = """
    MATCH (neo4j:Tag {name:'neo4j'})
    MATCH (p:Person)-[:REGISTERED]->(u:User:Twitter)-[:POSTED]->(t:Tweet)-[:TAGGED]->(tag:Tag {name:'contrib'})
    USING INDEX tag:Tag(name)
    WHERE NOT t:Contribution AND (t)-[:TAGGED]->(neo4j)
    SET t:Contribution
    WITH *
    OPTIONAL MATCH (t)-[:LINKED]->(l:Link)<-[:LINKED]-(c:Content) WHERE NOT c:Tweet
    WITH p, t, coalesce(c,l,t) as target
    MERGE (p)-[r:CONTRIBUTED]->(target) ON CREATE SET r.created = t.created
    """
  results = session.run(query)
  results.consume()

def add_contribution(userId, url, type, time, description): 
  session = db_driver.session()
  query = """
    MATCH (p:Person {id:{id}})
    MERGE (l:Link {url:{url}) ON CREATE SET l.title = {description}, l.cleanedUrl = {url}
    MERGE (l)<-[:LINKED]-(c:Content) ON CREATE SET c.title = {description}
    SET c:Contribution, c.review = true
    WITH coalesce(c,l) as target
    MERGE (p)-[r:CONTRIBUTED]->(target) SET r.created = coalesce(target.created, timestamp()/1000), r.description = {description}
    """
  results = session.run(query, parameters={"id": userId, "badge":badge, "score":score, "description":description})
  results.consume()


def get_profile(userId):
  session = db_driver.session()
  query = """
    MATCH (p:Person {id:{id}})
    RETURN p { .* } as profile, 
      [(p)-[r:WORKED_AT]->(c) | r { company: c.name, .since, .title}] as companies, 
      [(p)-[r:REGISTERED]->(u) |  { id: case when u:Twitter then u.screen_name when u:GitHub then u.name else u.id end, 
                                     account: [l in labels(u) WHERE NOT l IN ['User']]}] as accounts,
      [(p)-[r:ACHIEVED]->(b) | b { .*, score:r.score, created:r.created}] as badges 
    """
  results = 
  for record in session.run(query, parameters={"id": userId}) :
    return dict(record)

def get_activities(userId, limit = 100):
  session = db_driver.session()
  query = """
    MATCH (p:Person {id:{id}})-[r:CONTRIBUTED]->(contrib)
    OPTIONAL MATCH (contrib)-[:LINKED]->(l:Link)
    RETURN r.created as created, contrib.title as description, r.cleanedUrl as url
    ORDER BY created DESC LIMIT {limit}
    """
  results = session.run(query, parameters={"id": userId, "limit": limit})
  return [dict(record) for record in results]