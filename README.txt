# Useful link:
http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask

# To install flask:
sudo aptitude install python-flask

# To run some quick tests:

  # run the server
  python bin/dbServer.py

  # and run some queries:
  curl http://localhost:5000/db
  curl http://localhost:5000/db/v0
  curl http://localhost:5000/db/v0/query
  curl http://localhost:5000/db/v0/query?sql='show+databases+like+"%Stripe%"'
  curl http://localhost:5000/db/v0/query?sql=SELECT+COUNT\(*\)+FROM+jacek_1mRows.Source
  curl http://localhost:5000/db/v0/query?sql=SELECT+deepSourceId+FROM+jacek_1mRows.Source+limit+10
