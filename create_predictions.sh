for i in {1..25}; do
  curl -s -X POST http://localhost:8080/predict \
    -H "Content-Type: application/json" \
    -d '{"text": "Amazing movie, loved it!"}' > /dev/null
  echo -n "."
done

for i in {1..25}; do
  curl -s -X POST http://localhost:8080/predict \
    -H "Content-Type: application/json" \
    -d '{"text": "Terrible, do not watch"}' > /dev/null
  echo -n "."
done

echo ""
echo "Done! Check metrics:"
curl -s http://localhost:8080/metrics | grep "model_predictions_total "