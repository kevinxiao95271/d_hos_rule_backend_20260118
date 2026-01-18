#!/bin/bash
# Monitor batch progress

BATCH_KEY="2023_opt"
START_TIME=$(date +%s)

echo "=========================================="
echo "Monitoring Batch: $BATCH_KEY"
echo "Start Time: $(date)"
echo "=========================================="
echo ""

while true; do
    RESPONSE=$(curl -s "http://localhost:4101/api/qc/batch/status/$BATCH_KEY")

    PROGRESS=$(echo $RESPONSE | grep -o '"progress":[0-9]*' | grep -o '[0-9]*')
    STATUS=$(echo $RESPONSE | grep -o '"status":"[^"]*"' | sed 's/"status":"//;s/"//')

    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))

    echo "[$(date +%H:%M:%S)] Progress: ${PROGRESS}% | Status: ${STATUS} | Elapsed: ${ELAPSED}s"

    if [ "$STATUS" = "completed" ]; then
        echo ""
        echo "=========================================="
        echo "COMPLETED!"
        echo "Total Time: ${ELAPSED}s ($((ELAPSED/60))m $((ELAPSED%60))s)"
        echo "=========================================="
        echo ""
        echo "Full Response:"
        echo $RESPONSE | python -m json.tool 2>/dev/null || echo $RESPONSE
        break
    fi

    if [ "$STATUS" = "failed" ]; then
        echo ""
        echo "FAILED!"
        break
    fi

    sleep 5
done
