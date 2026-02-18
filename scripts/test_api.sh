#!/bin/bash
# API integration test script
# Usage: ./scripts/test_api.sh [base_url]
# Default base_url: http://localhost:8000/api

BASE_URL="${1:-http://localhost:8000/api}"
echo "Testing API at $BASE_URL"
echo "---"

# 1. Token (Login)
echo "1. POST $BASE_URL/token/ (Login)"
TOKEN_RESP=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/token/" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}')
HTTP_CODE=$(echo "$TOKEN_RESP" | tail -n1)
BODY=$(echo "$TOKEN_RESP" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
  TOKEN=$(echo "$BODY" | grep -o '"access":"[^"]*"' | cut -d'"' -f4)
  if [ -n "$TOKEN" ]; then
    echo "   OK - Got token"
  else
    echo "   FAIL - No token in response. Create a user first: python manage.py createsuperuser"
    exit 1
  fi
else
  echo "   FAIL - HTTP $HTTP_CODE"
  echo "$BODY" | head -5
  echo "   Create a user: python manage.py createsuperuser"
  exit 1
fi

# 2. Document Types (requires auth)
echo "2. GET $BASE_URL/document-types/"
DOC_TYPES=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/document-types/" \
  -H "Authorization: Bearer $TOKEN")
DOC_HTTP=$(echo "$DOC_TYPES" | tail -n1)
if [ "$DOC_HTTP" = "200" ]; then
  echo "   OK"
else
  echo "   FAIL - HTTP $DOC_HTTP"
fi

# 3. Create Document (requires auth + staff)
echo "3. POST $BASE_URL/create/"
DOC_TYPE_ID=$(echo "$DOC_TYPES" | sed '$d' | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
CREATE_RESP=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/create/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"document_type\":$DOC_TYPE_ID,\"metadata\":{\"name\":\"Test User\",\"courseName\":\"Test Course\",\"grade\":\"A\",\"date\":\"2024-01-15\"}}")
CREATE_HTTP=$(echo "$CREATE_RESP" | tail -n1)
CREATE_BODY=$(echo "$CREATE_RESP" | sed '$d')

if [ "$CREATE_HTTP" = "201" ]; then
  TRACKING=$(echo "$CREATE_BODY" | grep -o '"tracking_field":"[^"]*"' | cut -d'"' -f4)
  PDF_URL=$(echo "$CREATE_BODY" | grep -o '"pdf_url":"[^"]*"' | cut -d'"' -f4)
  echo "   OK - tracking_field=$TRACKING"
else
  echo "   FAIL - HTTP $CREATE_HTTP"
  echo "$CREATE_BODY" | head -3
fi

# 4. Verify Document
if [ -n "$TRACKING" ]; then
  echo "4. GET $BASE_URL/verify/$TRACKING/"
  VERIFY=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/verify/$TRACKING/")
  VERIFY_HTTP=$(echo "$VERIFY" | tail -n1)
  if [ "$VERIFY_HTTP" = "200" ]; then
    echo "   OK"
  else
    echo "   FAIL - HTTP $VERIFY_HTTP"
  fi

  # 5. Download PDF
  echo "5. GET $BASE_URL/documents/$TRACKING/download/"
  DL=$(curl -s -w "\n%{http_code}" -o /dev/null -X GET "$BASE_URL/documents/$TRACKING/download/")
  DL_HTTP=$(echo "$DL" | tail -n1)
  if [ "$DL_HTTP" = "200" ]; then
    echo "   OK"
  else
    echo "   FAIL - HTTP $DL_HTTP"
  fi
fi

# 6. Analytics
echo "6. GET $BASE_URL/analytics/"
ANALYTICS=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/analytics/" \
  -H "Authorization: Bearer $TOKEN")
A_HTTP=$(echo "$ANALYTICS" | tail -n1)
if [ "$A_HTTP" = "200" ]; then
  echo "   OK"
else
  echo "   FAIL - HTTP $A_HTTP"
fi

echo "---"
echo "API tests complete"
