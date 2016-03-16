# Useful link:
http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask

# To install flask:
sudo aptitude install python-flask

# To run some quick tests:

  # run the server
  python bin/dbServer.py

  # and run some queries:
  curl 'http://localhost:5000/'
  curl 'http://localhost:5000/tap'
  curl 'http://localhost:5000/tap/sync'
  curl -d 'query=SHOW+DATABASES+LIKE+"%Stripe%"' http://localhost:5000/tap/sync
  curl -d 'query=SHOW+TABLES+IN+DC_W13_Stripe82' http://localhost:5000/tap/sync
  curl -d 'query=DESCRIBE+DC_W13_Stripe82.DeepForcedSource' http://localhost:5000/tap/sync
  curl -d 'query=DESCRIBE+DC_W13_Stripe82.Science_Ccd_Exposure' http://localhost:5000/tap/sync
  curl -d 'query=SELECT+deepForcedSourceId,scienceCcdExposureId+FROM+DC_W13_Stripe82.DeepForcedSource+LIMIT+10' http://localhost:5000/tap/sync
  curl -d 'query=SELECT+ra,decl,filterName+FROM+DC_W13_Stripe82.Science_Ccd_Exposure+WHERE+scienceCcdExposureId=125230127' http://localhost:5000/tap/sync

  You can also use alternative Content types by adding the following flags to curl:
  -H "Accept: text/html"
  -H "Accept: application/x-votable+xml"
