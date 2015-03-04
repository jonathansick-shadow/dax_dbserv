# Useful link:
http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask

# To install flask:
sudo aptitude install python-flask

# To run some quick tests:

  # run the server
  python bin/dbServer.py

  # and run some queries:
  curl 'http://localhost:5000/db'
  curl 'http://localhost:5000/db/v0'
  curl 'http://localhost:5000/db/v0/query'
  curl 'http://localhost:5000/db/v0/query?sql=SHOW+DATABASES+LIKE+"%Stripe%"'
  curl 'http://localhost:5000/db/v0/query?sql=SHOW+TABLES+IN+DC_W13_Stripe82'
  curl 'http://localhost:5000/db/v0/query?sql=DESCRIBE+DC_W13_Stripe82.DeepForcedSource'
  curl 'http://localhost:5000/db/v0/query?sql=DESCRIBE+DC_W13_Stripe82.Science_Ccd_Exposure'
  curl 'http://localhost:5000/db/v0/query?sql=SELECT+deepForcedSourceId,scienceCcdExposureId+FROM+DC_W13_Stripe82.DeepForcedSource+LIMIT+10'
  curl 'http://localhost:5000/db/v0/query?sql=SELECT+ra,decl,filterName+FROM+DC_W13_Stripe82.Science_Ccd_Exposure+WHERE+scienceCcdExposureId=125230127'
 curl 'http://localhost:5000/image/v0/raw/cutout?ra=7.90481567257&dec=-0.299951669961&filter=r&width=30.0&height=45.0'
