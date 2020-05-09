term_opt=""

if [ -t 1 ]; then
  term_opt="-t"
fi

docker run  --rm -i $term_opt -v $(pwd)/app.py:/app.py shopify/python-api:latest python3 /app.py $@
