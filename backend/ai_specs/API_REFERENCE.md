**API Reference**
Base URL: `http://localhost:8000`
Primary API prefix: `/api/v1/`
Alias prefix: `/api/` for all `maps` and `captains` endpoints (same paths without `/api/v1/`).

**Auth Flow (JWT)**
1. Client verifies phone OTP with Firebase and receives `id_token`.
2. Call `POST /api/v1/auth/firebase/` to exchange for JWT.
3. Use `Authorization: Bearer <jwt>` for all protected endpoints.

**Common Headers**
- `Content-Type: application/json`
- `Authorization: Bearer <jwt>`

**Status Codes**
- 200 OK
- 201 Created
- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found

**Auth**
Endpoint: `POST /api/v1/auth/firebase/`
Purpose: Exchange Firebase `id_token` for backend JWT and auto-create user.
Method: POST
Required Headers:
`Content-Type: application/json`
Authentication: None
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id_token` | string | Yes | Firebase ID token |
| `role` | string | No | `USER`, `CAPTAIN`, `RESTAURANT`, `ADMIN` |
Example JSON Request:
```json
{
  "id_token": "<firebase_id_token>",
  "role": "USER"
}
```
Example JSON Response:
```json
{
  "token": "<jwt>",
  "user": {
    "_id": "<user_id>",
    "phone": "+919999999999",
    "role": "USER",
    "wallet_balance": 0,
    "is_active": true,
    "created_at": "2026-02-09T08:00:00Z"
  }
}
```
Error Cases:
- 400 Phone number not found in token
- 400 Invalid token

**Users**
Endpoint: `GET /api/v1/users/me/`
Purpose: Fetch current user profile.
Method: GET
Required Headers:
`Authorization: Bearer <jwt>`
Authentication: JWT (any role)
Request Body Schema: none
Example Request:
```
GET /api/v1/users/me/
```
Example JSON Response:
```json
{
  "user": {
    "_id": "<user_id>",
    "phone": "+919999999999",
    "role": "USER",
    "wallet_balance": 12000
  }
}
```
Error Cases:
- 401 Unauthorized

Endpoint: `POST /api/v1/users/fcm-token/`
Purpose: Register or update FCM device token for notifications.
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (any role)
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `fcm_token` | string | Yes | Firebase FCM token |
Example JSON Request:
```json
{
  "fcm_token": "<device_token>"
}
```
Example JSON Response:
```json
{
  "user": {
    "_id": "<user_id>",
    "fcm_token": "<device_token>"
  }
}
```
Error Cases:
- 400 Validation error
- 401 Unauthorized

**Captains**
Endpoint: `POST /api/v1/captains/online/`
Alias: `POST /api/v1/captain/online/`, `POST /api/captain/online/`
Purpose: Set captain online or offline state.
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (CAPTAIN)
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `is_online` | boolean | Yes | Online/offline |
Example JSON Request:
```json
{ "is_online": true }
```
Example JSON Response:
```json
{ "captain": { "user_id": "<captain_id>", "is_online": true } }
```
Error Cases:
- 401 Unauthorized
- 403 Role not allowed

Endpoint: `POST /api/v1/captains/location/`
Alias: `POST /api/v1/captain/location/`, `POST /api/v1/captain/location/update`, `POST /api/captain/location/update`
Purpose: Update captain GPS location (every 3 to 5 seconds). Broadcasts live updates.
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (CAPTAIN)
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `lat` | number | Yes | Latitude |
| `lng` | number | Yes | Longitude |
Example JSON Request:
```json
{ "lat": 12.9716, "lng": 77.5946 }
```
Example JSON Response:
```json
{ "captain": { "user_id": "<captain_id>", "location": { "type": "Point", "coordinates": [77.5946, 12.9716] } } }
```
Error Cases:
- 401 Unauthorized
- 403 Role not allowed

Endpoint: `POST /api/v1/captains/accept-job/`
Purpose: Accept a job offer (legacy alias to matching accept).
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (CAPTAIN)
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `job_type` | string | Yes | `ORDER` or `RIDE` |
| `job_id` | string | Yes | Order or ride id |
Example JSON Request:
```json
{ "job_type": "ORDER", "job_id": "<order_id>" }
```
Example JSON Response:
```json
{ "job": { "_id": "<order_id>", "job_status": "ASSIGNED" } }
```
Error Cases:
- 400 Job not offered to this captain
- 401 Unauthorized
- 403 Role not allowed

Endpoint: `POST /api/v1/captains/complete-job/`
Purpose: Complete an assigned job (legacy alias to matching complete).
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (CAPTAIN)
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `job_type` | string | Yes | `ORDER` or `RIDE` |
| `job_id` | string | Yes | Order or ride id |
Example JSON Request:
```json
{ "job_type": "ORDER", "job_id": "<order_id>" }
```
Example JSON Response:
```json
{ "job": { "_id": "<order_id>", "job_status": "COMPLETED" } }
```
Error Cases:
- 400 Captain not assigned to this job
- 401 Unauthorized
- 403 Role not allowed

**Restaurants**
Endpoint: `POST /api/v1/restaurants/`
Purpose: Create restaurant profile (includes pickup coordinates for delivery).
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (RESTAURANT)
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `name` | string | Yes | Restaurant name |
| `address` | string | No | Address |
| `phone` | string | No | Phone |
| `lat` | number | No | Latitude |
| `lng` | number | No | Longitude |
Example JSON Request:
```json
{ "name": "Biryani House", "address": "MG Road", "phone": "+919999999999", "lat": 12.97, "lng": 77.59 }
```
Example JSON Response:
```json
{ "restaurant": { "_id": "<restaurant_id>", "name": "Biryani House" } }
```
Error Cases:
- 401 Unauthorized
- 403 Role not allowed

Endpoint: `POST /api/v1/restaurants/{restaurant_id}/menu/`
Purpose: Add menu item.
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (RESTAURANT)
Path Params:
| Param | Type | Required | Notes |
| --- | --- | --- | --- |
| `restaurant_id` | string | Yes | Restaurant id |
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `name` | string | Yes | Item name |
| `price` | integer | Yes | Price in paise |
| `is_available` | boolean | No | Default true |
Example JSON Request:
```json
{ "name": "Chicken Biryani", "price": 25000, "is_available": true }
```
Example JSON Response:
```json
{ "menu_item": { "_id": "<menu_id>", "name": "Chicken Biryani" } }
```
Error Cases:
- 403 Not allowed
- 404 Restaurant not found

Endpoint: `GET /api/v1/restaurants/{restaurant_id}/menu/list/`
Purpose: List menu items (public).
Method: GET
Required Headers: none
Authentication: None
Path Params:
| Param | Type | Required | Notes |
| --- | --- | --- | --- |
| `restaurant_id` | string | Yes | Restaurant id |
Request Body Schema: none
Example Request:
```
GET /api/v1/restaurants/<restaurant_id>/menu/list/
```
Example JSON Response:
```json
{ "items": [{ "_id": "<menu_id>", "name": "Chicken Biryani", "price": 25000 }] }
```
Error Cases:
- 404 Restaurant not found

**Orders (Ride + Food)**
Food Orders
Endpoint: `POST /api/v1/orders/checkout/`
Purpose: Validate cart and compute totals plus surge.
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (USER)
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `restaurant_id` | string | Yes | Restaurant id |
| `items` | array | Yes | List of `{menu_item_id, quantity}` |
Example JSON Request:
```json
{
  "restaurant_id": "<restaurant_id>",
  "items": [{"menu_item_id": "<menu_id>", "quantity": 2}]
}
```
Example JSON Response:
```json
{
  "items": [{"menu_item_id": "<menu_id>", "quantity": 2, "total": 50000}],
  "subtotal": 50000,
  "surge_multiplier": 1.2,
  "surge_amount": 10000,
  "total": 60000
}
```
Error Cases:
- 400 Invalid restaurant id
- 400 Invalid item or quantity
- 404 Restaurant not found

Endpoint: `POST /api/v1/orders/`
Purpose: Create food order and start matching.
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (USER)
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `restaurant_id` | string | Yes | Restaurant id |
| `items` | array | Yes | List of `{menu_item_id, quantity}` |
| `payment_mode` | string | Yes | `RAZORPAY`, `COD`, `WALLET`, `WALLET_RAZORPAY` (also accepts `WALLET + RAZORPAY`) |
| `wallet_amount` | integer | No | Wallet usage in paise |
Example JSON Request:
```json
{
  "restaurant_id": "<restaurant_id>",
  "items": [{"menu_item_id": "<menu_id>", "quantity": 2}],
  "payment_mode": "WALLET_RAZORPAY",
  "wallet_amount": 5000
}
```
Example JSON Response:
```json
{
  "order": { "_id": "<order_id>", "status": "PENDING_PAYMENT", "amount_total": 60000 },
  "items": [{"menu_item_id": "<menu_id>", "quantity": 2, "total": 50000}],
  "razorpay_order": { "id": "order_abc" }
}
```
Error Cases:
- 400 Invalid payment mode
- 400 Invalid wallet amount
- 400 Insufficient wallet balance
- 404 Restaurant not found

Endpoint: `POST /api/v1/orders/verify-payment/`
Purpose: Verify Razorpay payment and mark order paid.
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (USER)
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `order_id` | string | Yes | Order id |
| `razorpay_order_id` | string | Yes | Razorpay order id |
| `razorpay_payment_id` | string | Yes | Razorpay payment id |
| `razorpay_signature` | string | Yes | Signature |
Example JSON Request:
```json
{
  "order_id": "<order_id>",
  "razorpay_order_id": "order_abc",
  "razorpay_payment_id": "pay_123",
  "razorpay_signature": "sig"
}
```
Example JSON Response:
```json
{ "order": { "_id": "<order_id>", "is_paid": true, "status": "PLACED" } }
```
Error Cases:
- 400 Invalid order id
- 400 Signature verification failed

Ride Requests
Endpoint: `POST /api/v1/rides/fare/`
Purpose: Estimate ride fare with surge.
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (USER)
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `pickup_lat` | number | Yes | Latitude |
| `pickup_lng` | number | Yes | Longitude |
| `dropoff_lat` | number | Yes | Latitude |
| `dropoff_lng` | number | Yes | Longitude |
Example JSON Request:
```json
{ "pickup_lat": 12.97, "pickup_lng": 77.59, "dropoff_lat": 12.93, "dropoff_lng": 77.61 }
```
Example JSON Response:
```json
{ "fare_base": 3000, "surge_multiplier": 1.2, "surge_amount": 600, "fare_total": 3600 }
```
Error Cases:
- 400 Validation error

Endpoint: `POST /api/v1/rides/`
Purpose: Create ride request and start matching.
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (USER)
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `pickup_lat` | number | Yes | Latitude |
| `pickup_lng` | number | Yes | Longitude |
| `dropoff_lat` | number | Yes | Latitude |
| `dropoff_lng` | number | Yes | Longitude |
| `payment_mode` | string | Yes | `RAZORPAY`, `WALLET`, `WALLET_RAZORPAY` (also accepts `WALLET + RAZORPAY`) |
| `wallet_amount` | integer | No | Wallet usage in paise |
Example JSON Request:
```json
{
  "pickup_lat": 12.97,
  "pickup_lng": 77.59,
  "dropoff_lat": 12.93,
  "dropoff_lng": 77.61,
  "payment_mode": "WALLET",
  "wallet_amount": 5000
}
```
Example JSON Response:
```json
{ "ride": { "_id": "<ride_id>", "status": "PENDING_PAYMENT" }, "razorpay_order": null }
```
Error Cases:
- 400 Invalid payment mode
- 400 Invalid wallet amount
- 400 Insufficient wallet balance

Endpoint: `POST /api/v1/rides/verify-payment/`
Purpose: Verify Razorpay payment and mark ride paid.
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (USER)
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `ride_id` | string | Yes | Ride id |
| `razorpay_order_id` | string | Yes | Razorpay order id |
| `razorpay_payment_id` | string | Yes | Razorpay payment id |
| `razorpay_signature` | string | Yes | Signature |
Example JSON Request:
```json
{
  "ride_id": "<ride_id>",
  "razorpay_order_id": "order_abc",
  "razorpay_payment_id": "pay_123",
  "razorpay_signature": "sig"
}
```
Example JSON Response:
```json
{ "ride": { "_id": "<ride_id>", "is_paid": true, "status": "REQUESTED" } }
```
Error Cases:
- 400 Invalid ride id
- 400 Signature verification failed

Endpoint: `POST /api/v1/rides/complete/`
Purpose: Complete a ride (captain action).
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (CAPTAIN)
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `ride_id` | string | Yes | Ride id |
Example JSON Request:
```json
{ "ride_id": "<ride_id>" }
```
Example JSON Response:
```json
{ "ride": { "_id": "<ride_id>", "status": "COMPLETED" } }
```
Error Cases:
- 404 Ride not found

**Matching Engine**
Endpoint: `POST /api/v1/jobs/create/`
Purpose: Start matching for an existing job.
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (USER or RESTAURANT)
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `job_type` | string | Yes | `ORDER` or `RIDE` |
| `job_id` | string | Yes | Order or ride id |
Example JSON Request:
```json
{ "job_type": "ORDER", "job_id": "<order_id>" }
```
Example JSON Response:
```json
{ "candidates": ["<captain_id>"] }
```
Error Cases:
- 400 Invalid job id
- 400 Job not found

Endpoint: `POST /api/v1/jobs/accept/`
Purpose: Captain accepts a matching offer.
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (CAPTAIN)
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `job_type` | string | Yes | `ORDER` or `RIDE` |
| `job_id` | string | Yes | Order or ride id |
Example JSON Request:
```json
{ "job_type": "RIDE", "job_id": "<ride_id>" }
```
Example JSON Response:
```json
{ "job": { "_id": "<ride_id>", "job_status": "ASSIGNED" } }
```
Error Cases:
- 400 Job not offered to this captain
- 400 Captain unavailable

Endpoint: `POST /api/v1/jobs/reject/`
Purpose: Captain rejects a matching offer.
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (CAPTAIN)
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `job_type` | string | Yes | `ORDER` or `RIDE` |
| `job_id` | string | Yes | Order or ride id |
Example JSON Request:
```json
{ "job_type": "ORDER", "job_id": "<order_id>" }
```
Example JSON Response:
```json
{ "rejected": true }
```
Error Cases:
- 400 Job not offered to this captain

Endpoint: `POST /api/v1/jobs/complete/`
Purpose: Complete a matching job and release captain.
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (CAPTAIN)
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `job_type` | string | Yes | `ORDER` or `RIDE` |
| `job_id` | string | Yes | Order or ride id |
Example JSON Request:
```json
{ "job_type": "ORDER", "job_id": "<order_id>" }
```
Example JSON Response:
```json
{ "job": { "_id": "<order_id>", "job_status": "COMPLETED" } }
```
Error Cases:
- 400 Captain not assigned to this job

**Wallet & Rewards**
Endpoint: `GET /api/v1/wallet/transactions/`
Purpose: List wallet transactions.
Method: GET
Required Headers:
`Authorization: Bearer <jwt>`
Authentication: JWT (any role)
Request Body Schema: none
Example Request:
```
GET /api/v1/wallet/transactions/
```
Example JSON Response:
```json
{ "transactions": [{ "amount": 5000, "type": "DEBIT", "reason": "FOOD_ORDER" }] }
```
Error Cases:
- 401 Unauthorized

Endpoint: `POST /api/v1/wallet/refund/`
Purpose: Refund wallet for a reference.
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (USER)
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `reference` | string | No | Order or ride id |
| `amount` | integer | Yes | Amount in paise |
| `reason` | string | Yes | Reason text |
| `source` | string | Yes | `FOOD`, `RIDE`, `REFUND` |
Example JSON Request:
```json
{ "reference": "<order_id>", "amount": 5000, "reason": "Order cancelled", "source": "FOOD" }
```
Example JSON Response:
```json
{ "transaction": { "type": "CREDIT", "is_refund": true, "amount": 5000 } }
```
Error Cases:
- 400 Refund failed

Endpoint: `GET /api/v1/wallet/analytics/{user_id}/`
Purpose: Wallet analytics (daily, weekly, monthly totals).
Method: GET
Required Headers:
`Authorization: Bearer <jwt>`
Authentication: JWT (USER can access self, ADMIN can access any)
Path Params:
| Param | Type | Required | Notes |
| --- | --- | --- | --- |
| `user_id` | string | Yes | User id |
Request Body Schema: none
Example Request:
```
GET /api/v1/wallet/analytics/<user_id>/
```
Example JSON Response:
```json
{ "analytics": { "totals": { "credits": 10000, "debits": 5000, "rewards": 1000, "refunds": 0 } } }
```
Error Cases:
- 403 Not allowed
- 404 User not found

**Payments**
Endpoint: `POST /api/v1/payments/razorpay/order/`
Purpose: Create Razorpay order.
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (any role)
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `amount` | integer | Yes | Amount in paise |
| `currency` | string | No | Default `INR` |
| `receipt` | string | Yes | Receipt id |
Example JSON Request:
```json
{ "amount": 15000, "currency": "INR", "receipt": "order_123" }
```
Example JSON Response:
```json
{ "razorpay_order": { "id": "order_abc", "status": "created" } }
```
Error Cases:
- 400 Razorpay error

Endpoint: `POST /api/v1/payments/razorpay/verify/`
Purpose: Verify Razorpay signature.
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (any role)
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `razorpay_order_id` | string | Yes | Order id |
| `razorpay_payment_id` | string | Yes | Payment id |
| `razorpay_signature` | string | Yes | Signature |
Example JSON Request:
```json
{ "razorpay_order_id": "order_abc", "razorpay_payment_id": "pay_123", "razorpay_signature": "sig" }
```
Example JSON Response:
```json
{ "verified": true }
```
Error Cases:
- 400 Signature verification failed

**Maps & Tracking**
Endpoint: `POST /api/v1/maps/route`
Alias: `POST /api/maps/route`
Purpose: Calculate route, return polyline and decoded points. Cached in MongoDB.
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (USER, CAPTAIN, RESTAURANT, ADMIN)
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `origin_lat` | number | Yes | Latitude |
| `origin_lng` | number | Yes | Longitude |
| `destination_lat` | number | Yes | Latitude |
| `destination_lng` | number | Yes | Longitude |
| `mode` | string | No | Default `driving` |
Example JSON Request:
```json
{ "origin_lat": 12.97, "origin_lng": 77.59, "destination_lat": 12.93, "destination_lng": 77.61 }
```
Example JSON Response:
```json
{
  "route": {
    "distance_m": 5200,
    "duration_s": 900,
    "duration_in_traffic_s": 1100,
    "polyline": "<encoded>",
    "points": [{"lat": 12.97, "lng": 77.59}],
    "cached": false
  }
}
```
Error Cases:
- 400 GOOGLE_MAPS_KEY not configured
- 400 Maps API error

Endpoint: `POST /api/v1/maps/eta`
Alias: `POST /api/maps/eta`
Purpose: Calculate ETA and distance (traffic-aware).
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (USER, CAPTAIN, RESTAURANT, ADMIN)
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `origin_lat` | number | Yes | Latitude |
| `origin_lng` | number | Yes | Longitude |
| `destination_lat` | number | Yes | Latitude |
| `destination_lng` | number | Yes | Longitude |
| `mode` | string | No | Default `driving` |
Example JSON Request:
```json
{ "origin_lat": 12.97, "origin_lng": 77.59, "destination_lat": 12.93, "destination_lng": 77.61 }
```
Example JSON Response:
```json
{ "eta": { "distance_m": 5200, "duration_s": 900, "duration_in_traffic_s": 1100 } }
```
Error Cases:
- 400 GOOGLE_MAPS_KEY not configured
- 400 Maps API error
- 400 No route found

Endpoint: `GET /api/v1/captain/nearby`
Alias: `GET /api/captain/nearby`
Purpose: Fetch nearby online captains using geo queries.
Method: GET
Required Headers:
`Authorization: Bearer <jwt>`
Authentication: JWT (USER, ADMIN)
Query Params:
| Param | Type | Required | Notes |
| --- | --- | --- | --- |
| `lat` | number | Yes | Latitude |
| `lng` | number | Yes | Longitude |
| `radius_m` | integer | No | Default 5000, min 100, max 20000 |
Request Body Schema: none
Example Request:
```
GET /api/v1/captain/nearby?lat=12.97&lng=77.59&radius_m=3000
```
Example JSON Response:
```json
{ "captains": [{ "user_id": "<captain_id>", "location": { "type": "Point", "coordinates": [77.59, 12.97] } }] }
```
Error Cases:
- 400 Validation error

Endpoint: `POST /api/v1/route/optimize/`
Purpose: Optimize routes using clustering and nearest-neighbor.
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (USER, CAPTAIN, RESTAURANT, ADMIN)
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `points` | array | Yes | List of `{lat,lng}` |
| `clusters` | integer | No | 1 to 10 |
Example JSON Request:
```json
{ "points": [{"lat": 12.97, "lng": 77.59}, {"lat": 12.95, "lng": 77.6}], "clusters": 2 }
```
Example JSON Response:
```json
{ "optimized": [{"lat": 12.97, "lng": 77.59}, {"lat": 12.95, "lng": 77.6}] }
```
Error Cases:
- 400 Validation error

WebSocket: `GET ws/captain/{captain_id}/`
Purpose: Captain receives job offers and status updates.
Method: GET (WebSocket upgrade)
Required Headers: none
Authentication: None enforced (client must use trusted captain id)
Path Params:
| Param | Type | Required | Notes |
| --- | --- | --- | --- |
| `captain_id` | string | Yes | Captain user id |
Request Body Schema: JSON messages
Example JSON Request:
```json
{ "type": "ping" }
```
Example JSON Response:
```json
{ "type": "pong" }
```
Server Push Examples:
```json
{ "type": "job_offer", "data": { "job_id": "<id>", "job_type": "ORDER" } }
```
Error Cases:
- Connection closed

WebSocket: `GET ws/user/{user_id}/`
Purpose: User receives job assignment, status, and live location updates.
Method: GET (WebSocket upgrade)
Required Headers: none
Authentication: None enforced (client must use trusted user id)
Path Params:
| Param | Type | Required | Notes |
| --- | --- | --- | --- |
| `user_id` | string | Yes | User id |
Request Body Schema: JSON messages
Example JSON Request:
```json
{ "type": "ping" }
```
Example JSON Response:
```json
{ "type": "pong" }
```
Server Push Examples:
```json
{ "type": "location_update", "data": { "job_id": "<id>", "job_type": "RIDE", "location": { "lat": 12.97, "lng": 77.59 } } }
```
Error Cases:
- Connection closed

WebSocket: `GET ws/order/{order_id}/`
Purpose: Order tracking channel for live location updates.
Method: GET (WebSocket upgrade)
Required Headers: none
Authentication: None enforced
Path Params:
| Param | Type | Required | Notes |
| --- | --- | --- | --- |
| `order_id` | string | Yes | Order id |
Request Body Schema: JSON messages
Example JSON Request:
```json
{ "type": "ping" }
```
Example JSON Response:
```json
{ "type": "pong" }
```
Server Push Examples:
```json
{ "type": "location_update", "data": { "job_id": "<id>", "job_type": "ORDER", "location": { "lat": 12.97, "lng": 77.59 } } }
```
Error Cases:
- Connection closed

**Surge Pricing**
Endpoint: `POST /api/v1/pricing/calculate/`
Purpose: Calculate surge multiplier for rides or food orders.
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (USER, CAPTAIN, RESTAURANT, ADMIN)
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `job_type` | string | Yes | `ORDER` or `RIDE` |
| `lat` | number | Yes | Latitude |
| `lng` | number | Yes | Longitude |
Example JSON Request:
```json
{ "job_type": "RIDE", "lat": 12.97, "lng": 77.59 }
```
Example JSON Response:
```json
{ "surge": { "surge_multiplier": 1.2, "demand": 10, "supply": 3, "time_factor": 0.2 } }
```
Error Cases:
- 400 Validation error

**Ratings**
Endpoint: `POST /api/v1/captain/rate/`
Purpose: Rate captain after completion.
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (USER)
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `job_type` | string | Yes | `ORDER` or `RIDE` |
| `job_id` | string | Yes | Order or ride id |
| `rating` | integer | Yes | 1 to 5 |
| `comment` | string | No | Optional text |
Example JSON Request:
```json
{ "job_type": "RIDE", "job_id": "<ride_id>", "rating": 5, "comment": "Great ride" }
```
Example JSON Response:
```json
{ "rating": { "captain_id": "<captain_id>", "rating": 5 } }
```
Error Cases:
- 400 Job not found
- 400 Order is not completed
- 400 Ride is not completed
- 400 Rating already submitted

Endpoint: `GET /api/v1/captain/{captain_id}/stats/`
Purpose: Fetch captain rating stats.
Method: GET
Required Headers:
`Authorization: Bearer <jwt>`
Authentication: JWT (any role)
Path Params:
| Param | Type | Required | Notes |
| --- | --- | --- | --- |
| `captain_id` | string | Yes | Captain user id |
Request Body Schema: none
Example Request:
```
GET /api/v1/captain/<captain_id>/stats/
```
Example JSON Response:
```json
{ "stats": { "captain_id": "<captain_id>", "average_rating": 4.9, "total_ratings": 120, "total_trips": 240, "cancellation_rate": 0.02 } }
```
Error Cases:
- 404 Captain not found

**Admin**
Endpoint: `GET /api/v1/admin/overview/`
Purpose: Admin analytics summary.
Method: GET
Required Headers:
`Authorization: Bearer <jwt>`
Authentication: JWT (ADMIN)
Request Body Schema: none
Example Request:
```
GET /api/v1/admin/overview/
```
Example JSON Response:
```json
{ "overview": { "total_users": 1200, "active_captains": 45, "revenue": 2500000, "surge_impact": 120000, "wallet_balances": 800000 } }
```
Error Cases:
- 403 Role not allowed

Endpoint: `GET /api/v1/admin/users/`
Purpose: List users.
Method: GET
Required Headers:
`Authorization: Bearer <jwt>`
Authentication: JWT (ADMIN)
Query Params:
| Param | Type | Required | Notes |
| --- | --- | --- | --- |
| `limit` | integer | No | Default 50 |
| `skip` | integer | No | Default 0 |
Request Body Schema: none
Example Request:
```
GET /api/v1/admin/users/?limit=50&skip=0
```
Example JSON Response:
```json
{ "users": [{ "_id": "<user_id>", "phone": "+919999999999" }] }
```
Error Cases:
- 403 Role not allowed

Endpoint: `GET /api/v1/admin/captains/`
Purpose: List captains.
Method: GET
Required Headers:
`Authorization: Bearer <jwt>`
Authentication: JWT (ADMIN)
Query Params:
| Param | Type | Required | Notes |
| --- | --- | --- | --- |
| `limit` | integer | No | Default 50 |
| `skip` | integer | No | Default 0 |
Request Body Schema: none
Example Request:
```
GET /api/v1/admin/captains/?limit=50&skip=0
```
Example JSON Response:
```json
{ "captains": [{ "user_id": "<captain_id>", "is_online": true }] }
```
Error Cases:
- 403 Role not allowed

Endpoint: `GET /api/v1/fraud/scan/`
Purpose: Scan for anomalous user activity (IsolationForest).
Method: GET
Required Headers:
`Authorization: Bearer <jwt>`
Authentication: JWT (ADMIN)
Query Params:
| Param | Type | Required | Notes |
| --- | --- | --- | --- |
| `limit` | integer | No | Default 200 |
Request Body Schema: none
Example Request:
```
GET /api/v1/fraud/scan/?limit=200
```
Example JSON Response:
```json
{ "suspicious": [{ "user_id": "<user_id>", "score": -0.12, "features": { "ride_count": 3 } }] }
```
Error Cases:
- 403 Role not allowed

Endpoint: `POST /api/v1/notifications/send/`
Purpose: Send FCM notification to a user.
Method: POST
Required Headers:
`Content-Type: application/json`
`Authorization: Bearer <jwt>`
Authentication: JWT (any role)
Request Body Schema:
| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `user_id` | string | Yes | Target user id |
| `title` | string | Yes | Notification title |
| `body` | string | Yes | Notification body |
| `data` | object | No | Extra metadata |
Example JSON Request:
```json
{ "user_id": "<user_id>", "title": "Order placed", "body": "Your order is being prepared", "data": {"order_id": "<id>"} }
```
Example JSON Response:
```json
{ "sent": true }
```
Error Cases:
- 400 Validation error
