WITH {member:"Community Member", certified:"Certified Developer",contributor:"Community Contributor",
      leader:"Community Leader",trainer:"Trainer", ambassador:"Ambassador"} as badges
UNWIND keys(badges) as name
MERGE (:Badge {name:name}) ON CREATE SET b.description = badges[name];

create index on :Link(cleanedUrl);
