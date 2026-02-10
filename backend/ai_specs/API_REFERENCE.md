# GoRides API Reference

Base URL: `/api/v1/` (Legacy: Maps and Captain endpoints are also available under `/api/`).
Authentication: JWT via `Authorization: Bearer <jwt>` for protected endpoints.
Roles: USER, CAPTAIN, RESTAURANT, ADMIN.
Amounts are integer paise unless noted. Timestamps are ISO 8601 (UTC).

**Public APIs**
Auth
Endpoint: POST /api/v1/auth/firebase/

Purpose:
Login with Firebase ID token and issue a GoRides JWT.

Method: POST

Authentication: None

Headers:
Content-Type: application/json

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| id_token | string | Yes | Firebase ID token |
| role | string | No | USER, CAPTAIN, RESTAURANT, ADMIN |

Example Request:
```json
{
  "id_token": "firebase_id_token",
  "role": "USER"
}
```

Example Response:
```json
{
  "token": "<jwt>",
  "user": {
    "_id": "65c7f7d0e9f1c3a1b2c3d4e5",
    "phone": "+919999999999",
    "role": "USER",
    "created_at": "2026-02-10T10:15:30.000Z"
  }
}
```

Status Codes:
200 OK
400 Bad Request

Error Cases:
Invalid or missing id_token
Phone number not found in token

Notes:
If the user does not exist, it is created. If role is CAPTAIN, a captain profile is created.

Restaurants & Menu (Public)
Endpoint: GET /api/v1/restaurants/{restaurant_id}/menu/list/

Purpose:
List available menu items for a restaurant.

Method: GET

Authentication: None

Headers:
None

Path Params:
| Param | Type | Required | Notes |
| restaurant_id | string | Yes | Restaurant id |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "items": [
    {
      "_id": "65c7f8a7e9f1c3a1b2c3d4e6",
      "restaurant_id": "65c7f7fbe9f1c3a1b2c3d4e7",
      "name": "Chicken Biryani",
      "price": 25000,
      "is_available": true
    }
  ]
}
```

Status Codes:
200 OK

Error Cases:
None (invalid restaurant_id returns empty list)

Notes:
Public endpoint.

Restaurants (Public)
Endpoint: GET /api/v1/restaurants/recommended/

Purpose:
List recommended restaurants.

Method: GET

Authentication: None

Headers:
None

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| limit | integer | No | Default 50 |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "restaurants": [
    {
      "_id": "65c7f7fbe9f1c3a1b2c3d4e7",
      "name": "Biryani House",
      "address": "MG Road",
      "is_recommended": true
    }
  ]
}
```

Status Codes:
200 OK

Error Cases:
None

Notes:
Public endpoint.

Menu (Public)
Endpoint: GET /api/v1/menu/recommended/

Purpose:
List recommended menu items across restaurants.

Method: GET

Authentication: None

Headers:
None

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| limit | integer | No | Default 50 |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "items": [
    {
      "_id": "65c7f8a7e9f1c3a1b2c3d4e6",
      "restaurant_id": "65c7f7fbe9f1c3a1b2c3d4e7",
      "name": "Paneer Tikka",
      "price": 18000,
      "is_recommended": true
    }
  ]
}
```

Status Codes:
200 OK

Error Cases:
None

Notes:
Public endpoint.

Recommendations (Public)
Endpoint: GET /api/v1/recommendations/

Purpose:
List legacy recommendations feed.

Method: GET

Authentication: None

Headers:
None

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "recommendations": [
    {
      "_id": "65c7fb2de9f1c3a1b2c3d4f0",
      "type": "RESTAURANT",
      "reference_id": "65c7f7fbe9f1c3a1b2c3d4e7",
      "title": "Top Rated",
      "description": "Chef specials",
      "created_at": "2026-02-10T10:20:00.000Z"
    }
  ]
}
```

Status Codes:
200 OK

Error Cases:
None

Notes:
Public endpoint.

**Shared Authenticated APIs**
Users
Endpoint: GET /api/v1/users/me/

Purpose:
Fetch the authenticated user profile.

Method: GET

Authentication: JWT (USER/CAPTAIN/RESTAURANT/ADMIN)

Headers:
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "user": {
    "_id": "65c7f7d0e9f1c3a1b2c3d4e5",
    "phone": "+919999999999",
    "role": "USER",
    "wallet_balance": 12000,
    "reward_points": 150
  }
}
```

Status Codes:
200 OK
401 Unauthorized

Error Cases:
Invalid or missing JWT

Notes:
Returns the current user document.

Users
Endpoint: POST /api/v1/users/fcm-token/

Purpose:
Register or update FCM device token for push notifications.

Method: POST

Authentication: JWT (USER/CAPTAIN/RESTAURANT/ADMIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| fcm_token | string | Yes | Device FCM token |

Example Request:
```json
{
  "fcm_token": "fcm_device_token"
}
```

Example Response:
```json
{
  "user": {
    "_id": "65c7f7d0e9f1c3a1b2c3d4e5",
    "fcm_token": "fcm_device_token"
  }
}
```

Status Codes:
200 OK
401 Unauthorized

Error Cases:
Invalid or missing JWT

Notes:
Used by all roles for notifications.

Payments (Razorpay)
Endpoint: POST /api/v1/payments/razorpay/order/

Purpose:
Create a Razorpay order for a payment amount.

Method: POST

Authentication: JWT (USER/CAPTAIN/RESTAURANT/ADMIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| amount | integer | Yes | Amount in paise |
| currency | string | No | Default INR |
| receipt | string | Yes | Receipt reference |

Example Request:
```json
{
  "amount": 15000,
  "currency": "INR",
  "receipt": "order_65c7f9b3e9f1c3a1b2c3d4f1"
}
```

Example Response:
```json
{
  "razorpay_order": {
    "id": "order_abc123",
    "amount": 15000,
    "currency": "INR",
    "status": "created",
    "receipt": "order_65c7f9b3e9f1c3a1b2c3d4f1"
  }
}
```

Status Codes:
201 Created
400 Bad Request
401 Unauthorized

Error Cases:
Razorpay keys not configured
Invalid amount

Notes:
Used by both food orders and rides when payment_amount > 0.

Payments (Razorpay)
Endpoint: POST /api/v1/payments/razorpay/verify/

Purpose:
Verify a Razorpay payment signature.

Method: POST

Authentication: JWT (USER/CAPTAIN/RESTAURANT/ADMIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| razorpay_order_id | string | Yes | Razorpay order id |
| razorpay_payment_id | string | Yes | Razorpay payment id |
| razorpay_signature | string | Yes | Razorpay signature |

Example Request:
```json
{
  "razorpay_order_id": "order_abc123",
  "razorpay_payment_id": "pay_123",
  "razorpay_signature": "sig_xyz"
}
```

Example Response:
```json
{
  "verified": true
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized

Error Cases:
Signature verification failed

Notes:
Typically used internally by order/ride verification endpoints.

Pricing & Surge
Endpoint: POST /api/v1/pricing/calculate/

Purpose:
Calculate surge multiplier for a location and job type.

Method: POST

Authentication: JWT (USER/CAPTAIN/RESTAURANT/ADMIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| job_type | string | Yes | ORDER or RIDE |
| lat | number | Yes | Latitude |
| lng | number | Yes | Longitude |

Example Request:
```json
{
  "job_type": "RIDE",
  "lat": 12.9716,
  "lng": 77.5946
}
```

Example Response:
```json
{
  "surge": {
    "surge_multiplier": 1.2,
    "demand_score": 0.78,
    "created_at": "2026-02-10T10:22:10.000Z"
  }
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized

Error Cases:
Invalid job_type

Notes:
Used by ride and food pricing engines.

Maps & Routing
Endpoint: POST /api/v1/maps/route

Purpose:
Get route details between two points using Google Maps.

Method: POST

Authentication: JWT (USER/CAPTAIN/RESTAURANT/ADMIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| origin_lat | number | Yes | Latitude |
| origin_lng | number | Yes | Longitude |
| destination_lat | number | Yes | Latitude |
| destination_lng | number | Yes | Longitude |
| mode | string | No | driving, walking, two_wheeler |

Example Request:
```json
{
  "origin_lat": 12.9716,
  "origin_lng": 77.5946,
  "destination_lat": 12.9352,
  "destination_lng": 77.6245,
  "mode": "driving"
}
```

Example Response:
```json
{
  "route": {
    "distance_m": 5200,
    "duration_s": 960,
    "polyline": "_p~iF~ps|U_ulLnnqC_mqNvxq`@"
  }
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized

Error Cases:
Google Maps error

Notes:
Also available under legacy base `/api/maps/route`.

Maps & Routing
Endpoint: POST /api/v1/maps/eta

Purpose:
Get ETA between two points using Google Maps.

Method: POST

Authentication: JWT (USER/CAPTAIN/RESTAURANT/ADMIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| origin_lat | number | Yes | Latitude |
| origin_lng | number | Yes | Longitude |
| destination_lat | number | Yes | Latitude |
| destination_lng | number | Yes | Longitude |
| mode | string | No | driving, walking, two_wheeler |

Example Request:
```json
{
  "origin_lat": 12.9716,
  "origin_lng": 77.5946,
  "destination_lat": 12.9352,
  "destination_lng": 77.6245
}
```

Example Response:
```json
{
  "eta": {
    "distance_m": 5200,
    "duration_s": 900,
    "duration_in_traffic_s": 1050
  }
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized

Error Cases:
Google Maps error

Notes:
Also available under legacy base `/api/maps/eta`.

Maps & Routing
Endpoint: GET /api/v1/captain/nearby

Purpose:
Find nearby captains for a location.

Method: GET

Authentication: JWT (USER/ADMIN)

Headers:
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| lat | number | Yes | Latitude |
| lng | number | Yes | Longitude |
| radius_m | integer | No | Default 5000 (100 to 20000) |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "captains": [
    {
      "_id": "65c8001de9f1c3a1b2c3d4f2",
      "user_id": "65c7f7d0e9f1c3a1b2c3d4e8",
      "location": {"type": "Point", "coordinates": [77.5946, 12.9716]},
      "vehicle_type": "BIKE_PETROL",
      "is_online": true
    }
  ]
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized

Error Cases:
Invalid coordinates

Notes:
Also available under legacy base `/api/captain/nearby`.

Routing
Endpoint: POST /api/v1/route/optimize/

Purpose:
Optimize the order of multiple points for routing.

Method: POST

Authentication: JWT (USER/CAPTAIN/RESTAURANT/ADMIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| points | array<object> | Yes | [{lat, lng}] |
| clusters | integer | No | 1 to 10 |

Example Request:
```json
{
  "points": [
    {"lat": 12.97, "lng": 77.59},
    {"lat": 12.95, "lng": 77.60},
    {"lat": 12.96, "lng": 77.58}
  ],
  "clusters": 2
}
```

Example Response:
```json
{
  "optimized": [
    {"lat": 12.97, "lng": 77.59},
    {"lat": 12.96, "lng": 77.58},
    {"lat": 12.95, "lng": 77.60}
  ]
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized

Error Cases:
Invalid points

Notes:
Uses clustering when many points are provided.

ETA
Endpoint: POST /api/v1/eta/predict

Purpose:
Predict ETA with prep time, batch size, and traffic/weather factors.

Method: POST

Authentication: JWT (USER/CAPTAIN/RESTAURANT/ADMIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| origin_lat | number | Yes | Latitude |
| origin_lng | number | Yes | Longitude |
| destination_lat | number | Yes | Latitude |
| destination_lng | number | Yes | Longitude |
| prep_time_min | integer | No | Default 0 |
| batch_size | integer | No | Default 1 |
| traffic_factor | number | No | Default 1.0 |
| weather_factor | number | No | Default 1.0 |

Example Request:
```json
{
  "origin_lat": 12.9716,
  "origin_lng": 77.5946,
  "destination_lat": 12.9352,
  "destination_lng": 77.6245,
  "prep_time_min": 15,
  "batch_size": 2,
  "traffic_factor": 1.2,
  "weather_factor": 1.1
}
```

Example Response:
```json
{
  "eta": {
    "base_duration_s": 900,
    "adjusted_duration_s": 1710,
    "distance_m": 5200,
    "prep_time_min": 15,
    "batch_size": 2
  }
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized

Error Cases:
Invalid coordinates

Notes:
Used by SLA/ETA and dispatch.

Trust & Safety
Endpoint: POST /api/v1/trust/device/register

Purpose:
Register device fingerprint and metadata for trust scoring.

Method: POST

Authentication: JWT (USER/CAPTAIN/RESTAURANT/ADMIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| device_id | string | Yes | Device identifier |
| platform | string | No | android, ios, web |
| fingerprint | string | No | Device fingerprint hash |
| ip | string | No | IP address |
| meta | object | No | GPS and device metadata |

Example Request:
```json
{
  "device_id": "device-123",
  "platform": "android",
  "fingerprint": "hash",
  "ip": "203.0.113.1",
  "meta": {"mock_location": false, "location_speed_kmh": 34}
}
```

Example Response:
```json
{
  "device": {
    "_id": "65c802dfe9f1c3a1b2c3d4f3",
    "user_id": "65c7f7d0e9f1c3a1b2c3d4e5",
    "device_id": "device-123",
    "platform": "android",
    "created_at": "2026-02-10T10:30:00.000Z"
  }
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized

Error Cases:
Invalid payload

Notes:
Used for spoofing and duplicate-account detection.

Cancellation & Compensation
Endpoint: GET /api/v1/cancel/policy

Purpose:
Fetch current cancellation policy percentages.

Method: GET

Authentication: JWT (USER/CAPTAIN/RESTAURANT/ADMIN)

Headers:
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "policy": {
    "user_cancel_before_assign_refund_pct": 1.0,
    "user_cancel_after_assign_refund_pct": 0.5,
    "captain_cancel_penalty_pct": 0.1,
    "late_delivery_refund_pct": 0.2,
    "no_show_fee_pct": 0.1
  }
}
```

Status Codes:
200 OK
401 Unauthorized

Error Cases:
Invalid or missing JWT

Notes:
Policy is used by cancel/order and cancel/ride.

Chat & Calling
Endpoint: GET /api/v1/chat/history/{room_id}

Purpose:
Get recent chat messages for a room.

Method: GET

Authentication: JWT (USER/CAPTAIN/RESTAURANT/ADMIN)

Headers:
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| room_id | string | Yes | Chat room id |

Query Params:
| Param | Type | Required | Notes |
| limit | integer | No | Default 50, max 200 |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "messages": [
    {
      "_id": "65c80544e9f1c3a1b2c3d4f4",
      "room_id": "room_123",
      "sender_id": "65c7f7d0e9f1c3a1b2c3d4e5",
      "sender_role": "USER",
      "text": "On my way",
      "created_at": "2026-02-10T10:32:00.000Z"
    }
  ]
}
```

Status Codes:
200 OK
401 Unauthorized
403 Forbidden

Error Cases:
Not a participant of the room

Notes:
Only room participants can access history.

Chat & Calling
Endpoint: GET /api/v1/chat/call/{room_id}

Purpose:
Fetch masked calling numbers for a chat room.

Method: GET

Authentication: JWT (USER/CAPTAIN/RESTAURANT)

Headers:
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| room_id | string | Yes | Chat room id |

Query Params:
| Param | Type | Required | Notes |
| callee_id | string | Yes | Target user/captain/restaurant id |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "call": {
    "caller": "+91-70000-00001",
    "callee": "+91-70000-00002",
    "room_id": "room_123"
  }
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized
403 Forbidden

Error Cases:
callee_id missing
Not a participant of the room

Notes:
Masked numbers are generated by backend policy.

Campaigns
Endpoint: GET /api/v1/campaigns/active

Purpose:
List active marketing campaigns.

Method: GET

Authentication: JWT (USER/CAPTAIN/RESTAURANT/ADMIN)

Headers:
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| limit | integer | No | Default 50 |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "campaigns": [
    {
      "_id": "65c8065de9f1c3a1b2c3d4f5",
      "title": "EV Bonus Week",
      "active": true,
      "starts_at": "2026-02-10T00:00:00.000Z",
      "ends_at": "2026-02-17T00:00:00.000Z"
    }
  ]
}
```

Status Codes:
200 OK
401 Unauthorized

Error Cases:
Invalid or missing JWT

Notes:
Campaign rules are applied during checkout and ride creation.

Captain Stats
Endpoint: GET /api/v1/captain/{captain_id}/stats/

Purpose:
Get captain rating stats and aggregates.

Method: GET

Authentication: JWT (USER/CAPTAIN/RESTAURANT/ADMIN)

Headers:
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| captain_id | string | Yes | Captain user id |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "stats": {
    "captain_id": "65c7f7d0e9f1c3a1b2c3d4e8",
    "average_rating": 4.8,
    "total_ratings": 120,
    "total_trips": 540
  }
}
```

Status Codes:
200 OK
401 Unauthorized
404 Not Found

Error Cases:
Captain not found

Notes:
Aggregated stats for display in user/captain apps.

Vehicle Rules
Endpoint: GET /api/v1/vehicle/rules

Purpose:
Get current vehicle and EV reward rules.

Method: GET

Authentication: JWT (USER/CAPTAIN/RESTAURANT/ADMIN)

Headers:
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "rules": {
    "food_allowed_vehicles": ["BIKE_PETROL", "BIKE_EV"],
    "ev_reward_percentage": 0.1,
    "ev_bonus_multiplier": 1.0
  }
}
```

Status Codes:
200 OK
401 Unauthorized

Error Cases:
Invalid or missing JWT

Notes:
Food delivery is restricted to vehicles in food_allowed_vehicles.

Jobs & Matching
Endpoint: POST /api/v1/jobs/create/

Purpose:
Trigger matching for a job (food order or ride).

Method: POST

Authentication: JWT (USER/RESTAURANT)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| job_type | string | Yes | ORDER or RIDE |
| job_id | string | Yes | Order or ride id |

Example Request:
```json
{
  "job_type": "ORDER",
  "job_id": "65c80756e9f1c3a1b2c3d4f6"
}
```

Example Response:
```json
{
  "candidates": [
    "65c7f7d0e9f1c3a1b2c3d4e8",
    "65c7f7d0e9f1c3a1b2c3d4e9"
  ]
}
```

Status Codes:
201 Created
400 Bad Request
401 Unauthorized

Error Cases:
Job not found
Invalid job_type

Notes:
Matching enforces food delivery two-wheeler-only and ride vehicle_type matching. Go-Home captains receive only route-compatible jobs.

**User APIs**
Wallet
Endpoint: GET /api/v1/wallet/transactions/

Purpose:
List wallet transactions for the authenticated user.

Method: GET

Authentication: JWT (USER)

Headers:
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "transactions": [
    {
      "_id": "65c80848e9f1c3a1b2c3d4f7",
      "amount": 5000,
      "type": "DEBIT",
      "reason": "FOOD_ORDER",
      "source": "FOOD",
      "balance_after": 20000,
      "created_at": "2026-02-10T10:40:00.000Z"
    }
  ]
}
```

Status Codes:
200 OK
401 Unauthorized

Error Cases:
Invalid or missing JWT

Notes:
Wallet is separate from reward points.

Wallet
Endpoint: POST /api/v1/wallet/refund/

Purpose:
Credit a wallet refund.

Method: POST

Authentication: JWT (USER)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| reference | string | No | Order/Ride id |
| amount | integer | Yes | Amount in paise |
| reason | string | Yes | Refund reason |
| source | string | Yes | FOOD, RIDE, REFUND |

Example Request:
```json
{
  "reference": "65c80756e9f1c3a1b2c3d4f6",
  "amount": 5000,
  "reason": "Order cancelled",
  "source": "FOOD"
}
```

Example Response:
```json
{
  "transaction": {
    "_id": "65c808f1e9f1c3a1b2c3d4f8",
    "amount": 5000,
    "type": "CREDIT",
    "reason": "Order cancelled",
    "source": "FOOD",
    "is_refund": true,
    "balance_after": 25000
  }
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized

Error Cases:
Refund failed

Notes:
Used by cancellation flows and admin adjustments.

Wallet Analytics
Endpoint: GET /api/v1/wallet/analytics/{user_id}/

Purpose:
Get wallet analytics for a user (self or admin).

Method: GET

Authentication: JWT (USER/ADMIN)

Headers:
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| user_id | string | Yes | User id |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "analytics": {
    "totals": {"credits": 50000, "debits": 38000, "rewards": 2000, "refunds": 1500},
    "daily": {"2026-02-10": {"credits": 5000, "debits": 2000, "rewards": 0, "refunds": 0}},
    "weekly": {"2026-W07": {"credits": 20000, "debits": 15000, "rewards": 500, "refunds": 300}},
    "monthly": {"2026-02": {"credits": 50000, "debits": 38000, "rewards": 2000, "refunds": 1500}}
  }
}
```

Status Codes:
200 OK
401 Unauthorized
403 Forbidden
404 Not Found

Error Cases:
User not found
Not allowed to access another user

Notes:
USER can only access their own analytics. ADMIN can access any user.

Orders (Food)
Endpoint: POST /api/v1/orders/checkout/

Purpose:
Preview food order totals, surge, rewards, and redemption.

Method: POST

Authentication: JWT (USER)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| restaurant_id | string | Yes | Restaurant id |
| items | array<object> | Yes | [{menu_item_id, quantity}] |
| redeem_points | integer | No | Reward points to redeem |

Example Request:
```json
{
  "restaurant_id": "65c7f7fbe9f1c3a1b2c3d4e7",
  "items": [{"menu_item_id": "65c7f8a7e9f1c3a1b2c3d4e6", "quantity": 2}],
  "redeem_points": 50
}
```

Example Response:
```json
{
  "items": [
    {"menu_item_id": "65c7f8a7e9f1c3a1b2c3d4e6", "name": "Chicken Biryani", "price": 25000, "quantity": 2, "total": 50000}
  ],
  "subtotal": 50000,
  "surge_multiplier": 1.1,
  "surge_amount": 5000,
  "total_before_rewards": 55000,
  "redeem_points_applied": 50,
  "redeem_amount": 5000,
  "reward_points_earned": 20,
  "total": 50000
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized

Error Cases:
Restaurant or menu item not found
Invalid items

Notes:
Reward points are earned only for recommended restaurants/items. Redemption uses 1 point = ?1.

Orders (Food)
Endpoint: POST /api/v1/orders/

Purpose:
Create a food order and trigger matching.

Method: POST

Authentication: JWT (USER)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| restaurant_id | string | Yes | Restaurant id |
| items | array<object> | Yes | [{menu_item_id, quantity}] |
| payment_mode | string | Yes | RAZORPAY, COD, WALLET, WALLET_RAZORPAY |
| wallet_amount | integer | No | Amount from wallet in paise |
| redeem_points | integer | No | Reward points to redeem |

Example Request:
```json
{
  "restaurant_id": "65c7f7fbe9f1c3a1b2c3d4e7",
  "items": [{"menu_item_id": "65c7f8a7e9f1c3a1b2c3d4e6", "quantity": 2}],
  "payment_mode": "WALLET_RAZORPAY",
  "wallet_amount": 10000,
  "redeem_points": 50
}
```

Example Response:
```json
{
  "order": {
    "_id": "65c809d9e9f1c3a1b2c3d4f9",
    "status": "PENDING_PAYMENT",
    "amount_total": 50000,
    "payment_amount": 40000,
    "reward_points_earned": 20,
    "surge_multiplier": 1.1,
    "captain_id": null
  },
  "items": [
    {"menu_item_id": "65c7f8a7e9f1c3a1b2c3d4e6", "name": "Chicken Biryani", "price": 25000, "quantity": 2, "total": 50000}
  ],
  "razorpay_order": {
    "id": "order_abc123",
    "amount": 40000,
    "currency": "INR",
    "status": "created"
  }
}
```

Status Codes:
201 Created
400 Bad Request
401 Unauthorized

Error Cases:
Invalid payment_mode
Insufficient wallet balance

Notes:
Matching for food orders only allows BIKE_PETROL and BIKE_EV captains. Rewards are credited after successful payment.

Orders (Food)
Endpoint: POST /api/v1/orders/verify-payment/

Purpose:
Verify Razorpay payment for a food order.

Method: POST

Authentication: JWT (USER)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| order_id | string | Yes | Order id |
| razorpay_order_id | string | Yes | Razorpay order id |
| razorpay_payment_id | string | Yes | Razorpay payment id |
| razorpay_signature | string | Yes | Razorpay signature |

Example Request:
```json
{
  "order_id": "65c809d9e9f1c3a1b2c3d4f9",
  "razorpay_order_id": "order_abc123",
  "razorpay_payment_id": "pay_123",
  "razorpay_signature": "sig_xyz"
}
```

Example Response:
```json
{
  "order": {
    "_id": "65c809d9e9f1c3a1b2c3d4f9",
    "is_paid": true,
    "status": "PLACED"
  }
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized

Error Cases:
Payment verification failed
Order not found

Notes:
Reward points for recommended items are credited after payment verification.

Rides
Endpoint: POST /api/v1/rides/fare/

Purpose:
Get fare estimate and EV reward preview for a ride.

Method: POST

Authentication: JWT (USER)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| pickup_lat | number | Yes | Latitude |
| pickup_lng | number | Yes | Longitude |
| dropoff_lat | number | Yes | Latitude |
| dropoff_lng | number | Yes | Longitude |
| vehicle_type | string | Yes | BIKE_PETROL, BIKE_EV, AUTO, CAR, SUV |

Example Request:
```json
{
  "pickup_lat": 12.9716,
  "pickup_lng": 77.5946,
  "dropoff_lat": 12.9352,
  "dropoff_lng": 77.6245,
  "vehicle_type": "BIKE_EV"
}
```

Example Response:
```json
{
  "fare_base": 80,
  "surge_multiplier": 1.2,
  "surge_amount": 16,
  "fare_total": 96,
  "reward_points_preview": 9
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized

Error Cases:
Invalid vehicle_type

Notes:
Rates per km: BIKE_PETROL/BIKE_EV=8, AUTO=12, CAR=18, SUV=25. EV rewards apply only to BIKE_EV.

Rides
Endpoint: POST /api/v1/rides/

Purpose:
Create a ride request and trigger matching.

Method: POST

Authentication: JWT (USER)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| pickup_lat | number | Yes | Latitude |
| pickup_lng | number | Yes | Longitude |
| dropoff_lat | number | Yes | Latitude |
| dropoff_lng | number | Yes | Longitude |
| vehicle_type | string | Yes | BIKE_PETROL, BIKE_EV, AUTO, CAR, SUV |
| payment_mode | string | Yes | RAZORPAY, WALLET, WALLET_RAZORPAY |
| wallet_amount | integer | No | Wallet amount in paise |
| redeem_points | integer | No | Reward points to redeem |

Example Request:
```json
{
  "pickup_lat": 12.9716,
  "pickup_lng": 77.5946,
  "dropoff_lat": 12.9352,
  "dropoff_lng": 77.6245,
  "vehicle_type": "BIKE_EV",
  "payment_mode": "WALLET_RAZORPAY",
  "wallet_amount": 2000,
  "redeem_points": 20
}
```

Example Response:
```json
{
  "ride": {
    "_id": "65c80b15e9f1c3a1b2c3d4fa",
    "status": "PENDING_PAYMENT",
    "vehicle_type": "BIKE_EV",
    "is_ev": true,
    "reward_points_earned": 9,
    "fare": 96,
    "payment_amount": 76
  },
  "razorpay_order": {
    "id": "order_ride_123",
    "amount": 7600,
    "currency": "INR",
    "status": "created"
  }
}
```

Status Codes:
201 Created
400 Bad Request
401 Unauthorized

Error Cases:
Invalid payment_mode
Insufficient wallet balance

Notes:
EV rewards are earned only for BIKE_EV and credited after ride completion.

Rides
Endpoint: POST /api/v1/rides/verify-payment/

Purpose:
Verify Razorpay payment for a ride.

Method: POST

Authentication: JWT (USER)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| ride_id | string | Yes | Ride id |
| razorpay_order_id | string | Yes | Razorpay order id |
| razorpay_payment_id | string | Yes | Razorpay payment id |
| razorpay_signature | string | Yes | Razorpay signature |

Example Request:
```json
{
  "ride_id": "65c80b15e9f1c3a1b2c3d4fa",
  "razorpay_order_id": "order_ride_123",
  "razorpay_payment_id": "pay_123",
  "razorpay_signature": "sig_xyz"
}
```

Example Response:
```json
{
  "ride": {
    "_id": "65c80b15e9f1c3a1b2c3d4fa",
    "is_paid": true,
    "status": "REQUESTED"
  }
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized

Error Cases:
Payment verification failed
Ride not found

Notes:
Ride enters matching after verification.

Promotions
Endpoint: POST /api/v1/coupon/apply

Purpose:
Apply a coupon code and calculate discount.

Method: POST

Authentication: JWT (USER)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| code | string | Yes | Coupon code |
| amount | integer | Yes | Amount in paise |
| job_type | string | Yes | ORDER or RIDE |

Example Request:
```json
{
  "code": "WELCOME",
  "amount": 25000,
  "job_type": "ORDER"
}
```

Example Response:
```json
{
  "coupon": {
    "code": "WELCOME",
    "discount": 5000,
    "amount": 25000,
    "payable": 20000
  }
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized

Error Cases:
Coupon not found or expired
Usage limit reached

Notes:
Coupons can be restricted by job_type and min_amount.

Promotions
Endpoint: POST /api/v1/referral/use

Purpose:
Apply a referral code and credit reward points.

Method: POST

Authentication: JWT (USER)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| referral_code | string | Yes | Referral code |

Example Request:
```json
{
  "referral_code": "GORIDES123"
}
```

Example Response:
```json
{
  "used": true
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized

Error Cases:
Referral already used
Invalid referral code

Notes:
Credits reward points to both referee and referrer when configured.

Ratings
Endpoint: POST /api/v1/captain/rate/

Purpose:
Rate a captain after a ride or food order.

Method: POST

Authentication: JWT (USER)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| job_type | string | Yes | ORDER or RIDE |
| job_id | string | Yes | Order or ride id |
| rating | integer | Yes | 1 to 5 |
| comment | string | No | Optional comment |

Example Request:
```json
{
  "job_type": "RIDE",
  "job_id": "65c80b15e9f1c3a1b2c3d4fa",
  "rating": 5,
  "comment": "Great ride"
}
```

Example Response:
```json
{
  "rating": {
    "_id": "65c80c72e9f1c3a1b2c3d4fb",
    "job_type": "RIDE",
    "job_id": "65c80b15e9f1c3a1b2c3d4fa",
    "rating": 5,
    "comment": "Great ride",
    "created_at": "2026-02-10T10:50:00.000Z"
  }
}
```

Status Codes:
201 Created
400 Bad Request
401 Unauthorized

Error Cases:
Invalid rating
Job not found

Notes:
Rating impacts captain average rating.

Cancellation
Endpoint: POST /api/v1/cancel/order

Purpose:
Cancel a food order with refund/penalty logic.

Method: POST

Authentication: JWT (USER/CAPTAIN/RESTAURANT/ADMIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| order_id | string | Yes | Order id |
| actor | string | No | USER, CAPTAIN, RESTAURANT, SYSTEM, ADMIN |
| reason | string | Yes | Cancellation reason |
| late_delivery | boolean | No | Apply late-delivery refund |
| no_show | boolean | No | Apply no-show fee |
| metadata | object | No | Additional context |

Example Request:
```json
{
  "order_id": "65c809d9e9f1c3a1b2c3d4f9",
  "reason": "User cancelled",
  "late_delivery": false,
  "no_show": false
}
```

Example Response:
```json
{
  "result": {
    "cancellation": {"job_type": "ORDER", "reason": "User cancelled"},
    "refund": {"amount": 25000, "method": "WALLET"},
    "penalty": null
  }
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized

Error Cases:
Order not found
Order already closed

Notes:
Refunds and penalties follow cancel policy. Late delivery triggers partial refund. No-show may charge user fee.

Cancellation
Endpoint: POST /api/v1/cancel/ride

Purpose:
Cancel a ride with refund/penalty logic.

Method: POST

Authentication: JWT (USER/CAPTAIN/ADMIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| ride_id | string | Yes | Ride id |
| actor | string | No | USER, CAPTAIN, SYSTEM, ADMIN |
| reason | string | Yes | Cancellation reason |
| no_show | boolean | No | Apply no-show fee |
| metadata | object | No | Additional context |

Example Request:
```json
{
  "ride_id": "65c80b15e9f1c3a1b2c3d4fa",
  "reason": "User cancelled",
  "no_show": false
}
```

Example Response:
```json
{
  "result": {
    "cancellation": {"job_type": "RIDE", "reason": "User cancelled"},
    "refund": {"amount": 80, "method": "WALLET"},
    "penalty": null
  }
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized

Error Cases:
Ride not found
Ride already closed

Notes:
Refunds and penalties follow cancel policy. No-show may charge user fee.

Growth
Endpoint: GET /api/v1/feed/personalized

Purpose:
Fetch a personalized feed for the user.

Method: GET

Authentication: JWT (USER)

Headers:
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| limit | integer | No | Default 50 |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "feed": [
    {
      "_id": "65c7fb2de9f1c3a1b2c3d4f0",
      "type": "RESTAURANT",
      "reference_id": "65c7f7fbe9f1c3a1b2c3d4e7",
      "title": "Top Rated"
    }
  ]
}
```

Status Codes:
200 OK
401 Unauthorized

Error Cases:
Invalid or missing JWT

Notes:
Feed is derived from recommendations and engagement history.

Growth
Endpoint: POST /api/v1/experiment/assign

Purpose:
Assign an experiment variant for a user.

Method: POST

Authentication: JWT (USER/ADMIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| experiment_key | string | Yes | Experiment key |
| variants | array<string> | Yes | Variant list |

Example Request:
```json
{
  "experiment_key": "homepage_v1",
  "variants": ["A", "B"]
}
```

Example Response:
```json
{
  "assignment": {
    "experiment_key": "homepage_v1",
    "variant": "A"
  }
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized

Error Cases:
No variants provided

Notes:
Assignment is deterministic per user.

**Captain APIs**
Captain Status
Endpoint: POST /api/v1/captains/online/

Purpose:
Set captain online/offline status.

Method: POST

Authentication: JWT (CAPTAIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| is_online | boolean | Yes | true or false |

Example Request:
```json
{
  "is_online": true
}
```

Example Response:
```json
{
  "captain": {
    "user_id": "65c7f7d0e9f1c3a1b2c3d4e8",
    "is_online": true,
    "is_verified": true
  }
}
```

Status Codes:
200 OK
401 Unauthorized
403 Forbidden

Error Cases:
Captain not verified

Notes:
Unverified captains cannot go online. Going offline disables Go-Home mode.

Captain Status
Endpoint: POST /api/v1/captain/online/

Purpose:
Alias endpoint for setting captain online/offline.

Method: POST

Authentication: JWT (CAPTAIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| is_online | boolean | Yes | true or false |

Example Request:
```json
{
  "is_online": false
}
```

Example Response:
```json
{
  "captain": {
    "user_id": "65c7f7d0e9f1c3a1b2c3d4e8",
    "is_online": false
  }
}
```

Status Codes:
200 OK
401 Unauthorized
403 Forbidden

Error Cases:
Captain not verified

Notes:
Functionally identical to `/captains/online/`.

Captain Location
Endpoint: POST /api/v1/captains/location/

Purpose:
Update captain current GPS location.

Method: POST

Authentication: JWT (CAPTAIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| lat | number | Yes | Latitude |
| lng | number | Yes | Longitude |

Example Request:
```json
{
  "lat": 12.9716,
  "lng": 77.5946
}
```

Example Response:
```json
{
  "captain": {
    "user_id": "65c7f7d0e9f1c3a1b2c3d4e8",
    "location": {"type": "Point", "coordinates": [77.5946, 12.9716]}
  }
}
```

Status Codes:
200 OK
401 Unauthorized

Error Cases:
Invalid coordinates

Notes:
GPS jump detection may ignore unrealistic updates. Updates go-home ETA if enabled.

Captain Location
Endpoint: POST /api/v1/captain/location/

Purpose:
Alias endpoint for updating captain GPS location.

Method: POST

Authentication: JWT (CAPTAIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| lat | number | Yes | Latitude |
| lng | number | Yes | Longitude |

Example Request:
```json
{
  "lat": 12.9716,
  "lng": 77.5946
}
```

Example Response:
```json
{
  "captain": {
    "user_id": "65c7f7d0e9f1c3a1b2c3d4e8",
    "location": {"type": "Point", "coordinates": [77.5946, 12.9716]}
  }
}
```

Status Codes:
200 OK
401 Unauthorized

Error Cases:
Invalid coordinates

Notes:
Functionally identical to `/captains/location/`.

Captain Location
Endpoint: POST /api/v1/captain/location/update

Purpose:
Alias endpoint for updating captain GPS location.

Method: POST

Authentication: JWT (CAPTAIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| lat | number | Yes | Latitude |
| lng | number | Yes | Longitude |

Example Request:
```json
{
  "lat": 12.9716,
  "lng": 77.5946
}
```

Example Response:
```json
{
  "captain": {
    "user_id": "65c7f7d0e9f1c3a1b2c3d4e8",
    "location": {"type": "Point", "coordinates": [77.5946, 12.9716]}
  }
}
```

Status Codes:
200 OK
401 Unauthorized

Error Cases:
Invalid coordinates

Notes:
Functionally identical to `/captains/location/`.

Captain Vehicle
Endpoint: POST /api/v1/captain/vehicle/register/

Purpose:
Register or update captain vehicle details.

Method: POST

Authentication: JWT (CAPTAIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| vehicle_type | string | Yes | BIKE_PETROL, BIKE_EV, AUTO, CAR, SUV |
| vehicle_number | string | Yes | Registration number |
| vehicle_brand | string | Yes | Brand/model |
| license_number | string | Yes | License number |
| rc_image | string | Yes | RC image URL |
| license_image | string | Yes | License image URL |

Example Request:
```json
{
  "vehicle_type": "BIKE_EV",
  "vehicle_number": "KA01AB1234",
  "vehicle_brand": "Ather",
  "license_number": "DL123456789",
  "rc_image": "https://cdn.example.com/rc.jpg",
  "license_image": "https://cdn.example.com/license.jpg"
}
```

Example Response:
```json
{
  "vehicle": {
    "vehicle_type": "BIKE_EV",
    "is_ev": true,
    "vehicle_number": "KA01AB1234",
    "is_verified": false
  },
  "captain": {
    "user_id": "65c7f7d0e9f1c3a1b2c3d4e8",
    "is_verified": false
  }
}
```

Status Codes:
200 OK
401 Unauthorized
404 Not Found

Error Cases:
Captain not found
Invalid vehicle_type

Notes:
Registering a vehicle resets verification and sets captain offline.

Vehicles (Captain)
Endpoint: POST /api/v1/vehicle/register

Purpose:
Register vehicle details in the vehicles collection and update captain profile.

Method: POST

Authentication: JWT (CAPTAIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| vehicle_type | string | Yes | BIKE_PETROL, BIKE_EV, AUTO, CAR, SUV |
| vehicle_number | string | Yes | Registration number |
| vehicle_brand | string | Yes | Brand/model |
| license_number | string | Yes | License number |
| rc_image | string | Yes | RC image URL |
| license_image | string | Yes | License image URL |

Example Request:
```json
{
  "vehicle_type": "BIKE_EV",
  "vehicle_number": "KA01AB1234",
  "vehicle_brand": "Ather",
  "license_number": "DL123456789",
  "rc_image": "https://cdn.example.com/rc.jpg",
  "license_image": "https://cdn.example.com/license.jpg"
}
```

Example Response:
```json
{
  "vehicle": {
    "vehicle_type": "BIKE_EV",
    "is_ev": true,
    "vehicle_number": "KA01AB1234",
    "vehicle_brand": "Ather",
    "license_number": "DL123456789",
    "rc_image": "https://cdn.example.com/rc.jpg",
    "license_image": "https://cdn.example.com/license.jpg",
    "is_verified": false
  }
}
```

Status Codes:
200 OK
401 Unauthorized
404 Not Found

Error Cases:
Captain not found
Invalid vehicle_type

Notes:
This endpoint also maintains the vehicles collection for analytics and rules.

Captain Vehicle
Endpoint: GET /api/v1/captain/vehicle/me/

Purpose:
Get the captain's vehicle details.

Method: GET

Authentication: JWT (CAPTAIN)

Headers:
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "vehicle": {
    "vehicle_type": "BIKE_EV",
    "is_ev": true,
    "vehicle_number": "KA01AB1234",
    "vehicle_brand": "Ather",
    "license_number": "DL123456789",
    "rc_image": "https://cdn.example.com/rc.jpg",
    "license_image": "https://cdn.example.com/license.jpg",
    "is_verified": true
  }
}
```

Status Codes:
200 OK
401 Unauthorized
404 Not Found

Error Cases:
Captain not found

Notes:
Vehicle verification is controlled by admin.

Captain Go-Home Mode
Endpoint: POST /api/v1/captain/go-home/enable

Purpose:
Enable go-home mode and set home location.

Method: POST

Authentication: JWT (CAPTAIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| lat | number | Yes | Home latitude |
| lng | number | Yes | Home longitude |

Example Request:
```json
{
  "lat": 17.385044,
  "lng": 78.486671
}
```

Example Response:
```json
{
  "captain": {
    "user_id": "65c7f7d0e9f1c3a1b2c3d4e8",
    "go_home_mode": true,
    "home_location": {"type": "Point", "coordinates": [78.486671, 17.385044]}
  }
}
```

Status Codes:
200 OK
401 Unauthorized
404 Not Found

Error Cases:
Captain not found
Invalid coordinates

Notes:
Matching will only offer jobs that lie near the route home or reduce ETA to home. WebSocket job offers include `go_home_job: true`.

Captain Go-Home Mode
Endpoint: POST /api/v1/captain/go-home/disable

Purpose:
Disable go-home mode for the captain.

Method: POST

Authentication: JWT (CAPTAIN)

Headers:
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "captain": {
    "user_id": "65c7f7d0e9f1c3a1b2c3d4e8",
    "go_home_mode": false
  }
}
```

Status Codes:
200 OK
401 Unauthorized
404 Not Found

Error Cases:
Captain not found

Notes:
Go-home mode is also auto-disabled when captain goes offline.

Captain Jobs
Endpoint: POST /api/v1/captains/accept-job/

Purpose:
Accept a job offer for a ride or order.

Method: POST

Authentication: JWT (CAPTAIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| job_type | string | Yes | ORDER or RIDE |
| job_id | string | Yes | Order or ride id |

Example Request:
```json
{
  "job_type": "ORDER",
  "job_id": "65c809d9e9f1c3a1b2c3d4f9"
}
```

Example Response:
```json
{
  "job": {
    "_id": "65c809d9e9f1c3a1b2c3d4f9",
    "status": "ASSIGNED",
    "captain_id": "65c7f7d0e9f1c3a1b2c3d4e8"
  }
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized

Error Cases:
Job not offered to this captain
Captain unavailable

Notes:
Enforces vehicle_type matching and food two-wheeler rules.

Captain Jobs
Endpoint: POST /api/v1/captains/complete-job/

Purpose:
Complete a job (order or ride) for the current captain.

Method: POST

Authentication: JWT (CAPTAIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| job_type | string | Yes | ORDER or RIDE |
| job_id | string | Yes | Order or ride id |

Example Request:
```json
{
  "job_type": "ORDER",
  "job_id": "65c809d9e9f1c3a1b2c3d4f9"
}
```

Example Response:
```json
{
  "job": {
    "_id": "65c809d9e9f1c3a1b2c3d4f9",
    "status": "DELIVERED"
  }
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized

Error Cases:
Job not found

Notes:
Completing an order triggers reward credit for recommended items.

Jobs (Captain)
Endpoint: POST /api/v1/jobs/accept/

Purpose:
Accept a job offer (matching engine endpoint).

Method: POST

Authentication: JWT (CAPTAIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| job_type | string | Yes | ORDER or RIDE |
| job_id | string | Yes | Order or ride id |

Example Request:
```json
{
  "job_type": "RIDE",
  "job_id": "65c80b15e9f1c3a1b2c3d4fa"
}
```

Example Response:
```json
{
  "job": {
    "_id": "65c80b15e9f1c3a1b2c3d4fa",
    "status": "ASSIGNED",
    "captain_id": "65c7f7d0e9f1c3a1b2c3d4e8"
  }
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized

Error Cases:
Job not offered to this captain

Notes:
Same core logic as `/captains/accept-job/`.

Jobs (Captain)
Endpoint: POST /api/v1/jobs/reject/

Purpose:
Reject a job offer.

Method: POST

Authentication: JWT (CAPTAIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| job_type | string | Yes | ORDER or RIDE |
| job_id | string | Yes | Order or ride id |

Example Request:
```json
{
  "job_type": "ORDER",
  "job_id": "65c809d9e9f1c3a1b2c3d4f9"
}
```

Example Response:
```json
{
  "rejected": true
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized

Error Cases:
Job not offered to this captain

Notes:
Rejected captains are skipped in matching.

Jobs (Captain)
Endpoint: POST /api/v1/jobs/complete/

Purpose:
Complete a job via matching engine.

Method: POST

Authentication: JWT (CAPTAIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| job_type | string | Yes | ORDER or RIDE |
| job_id | string | Yes | Order or ride id |

Example Request:
```json
{
  "job_type": "RIDE",
  "job_id": "65c80b15e9f1c3a1b2c3d4fa"
}
```

Example Response:
```json
{
  "job": {
    "_id": "65c80b15e9f1c3a1b2c3d4fa",
    "job_status": "COMPLETED"
  }
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized

Error Cases:
Job not found

Notes:
Completing a ride triggers EV reward credit if eligible.

Rides (Captain)
Endpoint: POST /api/v1/rides/complete/

Purpose:
Mark a ride as completed.

Method: POST

Authentication: JWT (CAPTAIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| ride_id | string | Yes | Ride id |

Example Request:
```json
{
  "ride_id": "65c80b15e9f1c3a1b2c3d4fa"
}
```

Example Response:
```json
{
  "ride": {
    "_id": "65c80b15e9f1c3a1b2c3d4fa",
    "status": "COMPLETED"
  }
}
```

Status Codes:
200 OK
401 Unauthorized
404 Not Found

Error Cases:
Ride not found

Notes:
Credits EV rewards when ride is EV and paid.

Captain Earnings
Endpoint: GET /api/v1/captain/earnings

Purpose:
Get captain wallet balance and details.

Method: GET

Authentication: JWT (CAPTAIN)

Headers:
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "wallet": {
    "captain_id": "65c7f7d0e9f1c3a1b2c3d4e8",
    "balance": 32000,
    "updated_at": "2026-02-10T10:55:00.000Z"
  }
}
```

Status Codes:
200 OK
401 Unauthorized

Error Cases:
Invalid or missing JWT

Notes:
Captain wallet is separate from user wallet.

Captain Payouts
Endpoint: POST /api/v1/captain/payout/request

Purpose:
Request a payout from captain wallet.

Method: POST

Authentication: JWT (CAPTAIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| amount | integer | Yes | Amount in paise |

Example Request:
```json
{
  "amount": 5000
}
```

Example Response:
```json
{
  "payout": {
    "captain_id": "65c7f7d0e9f1c3a1b2c3d4e8",
    "amount": 5000,
    "tds_amount": 50,
    "net_amount": 4950,
    "status": "PENDING"
  }
}
```

Status Codes:
201 Created
400 Bad Request
401 Unauthorized

Error Cases:
Insufficient balance

Notes:
TDS is currently 1% placeholder.

Captain Payouts
Endpoint: GET /api/v1/captain/payout/history

Purpose:
List captain payout requests.

Method: GET

Authentication: JWT (CAPTAIN)

Headers:
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| limit | integer | No | Default 50 |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "payouts": [
    {
      "captain_id": "65c7f7d0e9f1c3a1b2c3d4e8",
      "amount": 5000,
      "tds_amount": 50,
      "net_amount": 4950,
      "status": "PENDING",
      "requested_at": "2026-02-10T10:56:00.000Z"
    }
  ]
}
```

Status Codes:
200 OK
401 Unauthorized

Error Cases:
Invalid or missing JWT

Notes:
Pending payouts are processed by finance ops.

Captain Bank
Endpoint: POST /api/v1/captain/bank/link

Purpose:
Link or update captain bank account.

Method: POST

Authentication: JWT (CAPTAIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| account_number | string | Yes | Bank account number |
| ifsc | string | Yes | IFSC code |
| name | string | Yes | Account holder name |
| upi | string | No | UPI id |

Example Request:
```json
{
  "account_number": "1234567890",
  "ifsc": "HDFC0001234",
  "name": "Captain",
  "upi": "captain@upi"
}
```

Example Response:
```json
{
  "bank_account": {
    "captain_id": "65c7f7d0e9f1c3a1b2c3d4e8",
    "account_number": "1234567890",
    "ifsc": "HDFC0001234",
    "name": "Captain",
    "upi": "captain@upi"
  }
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized

Error Cases:
Invalid captain

Notes:
Bank details are required for payouts.

**Restaurant APIs**
Restaurants
Endpoint: POST /api/v1/restaurants/

Purpose:
Create a restaurant profile.

Method: POST

Authentication: JWT (RESTAURANT)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| name | string | Yes | Restaurant name |
| address | string | No | Address |
| phone | string | No | Contact number |
| lat | number | No | Latitude |
| lng | number | No | Longitude |

Example Request:
```json
{
  "name": "Biryani House",
  "address": "MG Road",
  "phone": "+919999999999",
  "lat": 12.9716,
  "lng": 77.5946
}
```

Example Response:
```json
{
  "restaurant": {
    "_id": "65c7f7fbe9f1c3a1b2c3d4e7",
    "name": "Biryani House",
    "owner_id": "65c7f7d0e9f1c3a1b2c3d4e5",
    "location": {"type": "Point", "coordinates": [77.5946, 12.9716]}
  }
}
```

Status Codes:
201 Created
401 Unauthorized

Error Cases:
Invalid payload

Notes:
Restaurant location is used for surge and matching.

Menu Items
Endpoint: POST /api/v1/restaurants/{restaurant_id}/menu/

Purpose:
Add a menu item for a restaurant.

Method: POST

Authentication: JWT (RESTAURANT)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| restaurant_id | string | Yes | Restaurant id |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| name | string | Yes | Item name |
| price | integer | Yes | Price in paise |
| is_available | boolean | No | Default true |

Example Request:
```json
{
  "name": "Chicken Biryani",
  "price": 25000,
  "is_available": true
}
```

Example Response:
```json
{
  "menu_item": {
    "_id": "65c7f8a7e9f1c3a1b2c3d4e6",
    "restaurant_id": "65c7f7fbe9f1c3a1b2c3d4e7",
    "name": "Chicken Biryani",
    "price": 25000,
    "is_available": true
  }
}
```

Status Codes:
201 Created
401 Unauthorized
403 Forbidden
404 Not Found

Error Cases:
Restaurant not found
Not allowed to modify another restaurant

Notes:
Use restaurant item toggle to enable/disable availability later.

Restaurant Ops
Endpoint: POST /api/v1/restaurant/order/update

Purpose:
Update restaurant order status and prep time.

Method: POST

Authentication: JWT (RESTAURANT)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| order_id | string | Yes | Order id |
| status | string | Yes | PREPARING, READY, etc |
| prep_time_min | integer | No | Estimated prep time |

Example Request:
```json
{
  "order_id": "65c809d9e9f1c3a1b2c3d4f9",
  "status": "PREPARING",
  "prep_time_min": 20
}
```

Example Response:
```json
{
  "order": {
    "_id": "65c809d9e9f1c3a1b2c3d4f9",
    "status": "PREPARING",
    "prep_time_min": 20
  }
}
```

Status Codes:
200 OK
401 Unauthorized
404 Not Found

Error Cases:
Order not found

Notes:
Updates restaurant_ops tracking collection for analytics.

Restaurant Ops
Endpoint: POST /api/v1/restaurant/item/toggle

Purpose:
Enable or disable a menu item.

Method: POST

Authentication: JWT (RESTAURANT)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| menu_item_id | string | Yes | Menu item id |
| is_available | boolean | Yes | true or false |

Example Request:
```json
{
  "menu_item_id": "65c7f8a7e9f1c3a1b2c3d4e6",
  "is_available": false
}
```

Example Response:
```json
{
  "menu_item": {
    "_id": "65c7f8a7e9f1c3a1b2c3d4e6",
    "is_available": false
  }
}
```

Status Codes:
200 OK
401 Unauthorized
404 Not Found

Error Cases:
Menu item not found

Notes:
Also updates inventory collection.

Restaurant Ops
Endpoint: GET /api/v1/restaurant/analytics

Purpose:
Get restaurant analytics and revenue.

Method: GET

Authentication: JWT (RESTAURANT)

Headers:
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| restaurant_id | string | Yes | Restaurant id |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "analytics": {
    "restaurant_id": "65c7f7fbe9f1c3a1b2c3d4e7",
    "total_orders": 120,
    "delivered_orders": 110,
    "revenue": 520000
  }
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized
404 Not Found

Error Cases:
restaurant_id missing
Restaurant not found

Notes:
Revenue is based on paid orders.

**Admin APIs**
Admin Overview
Endpoint: GET /api/v1/admin/overview/

Purpose:
Get platform KPIs for admin dashboard.

Method: GET

Authentication: JWT (ADMIN)

Headers:
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "overview": {
    "total_users": 12000,
    "active_captains": 450,
    "revenue": 8500000,
    "surge_impact": 320000,
    "wallet_balances": 1200000
  }
}
```

Status Codes:
200 OK
401 Unauthorized

Error Cases:
Invalid or missing JWT

Notes:
Aggregates food and ride revenue.

Admin Users
Endpoint: GET /api/v1/admin/users/

Purpose:
List users for admin management.

Method: GET

Authentication: JWT (ADMIN)

Headers:
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| limit | integer | No | Default 50 |
| skip | integer | No | Default 0 |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "users": [
    {"_id": "65c7f7d0e9f1c3a1b2c3d4e5", "phone": "+919999999999", "role": "USER"}
  ]
}
```

Status Codes:
200 OK
401 Unauthorized

Error Cases:
Invalid or missing JWT

Notes:
Paginated via limit/skip.

Admin Captains
Endpoint: GET /api/v1/admin/captains/

Purpose:
List captains for admin management.

Method: GET

Authentication: JWT (ADMIN)

Headers:
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| limit | integer | No | Default 50 |
| skip | integer | No | Default 0 |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "captains": [
    {"user_id": "65c7f7d0e9f1c3a1b2c3d4e8", "is_verified": false, "vehicle_type": "BIKE_EV"}
  ]
}
```

Status Codes:
200 OK
401 Unauthorized

Error Cases:
Invalid or missing JWT

Notes:
Use verify endpoint to approve or reject captains.

Admin Captains
Endpoint: GET /api/v1/admin/go-home-captains/

Purpose:
List captains currently in go-home mode.

Method: GET

Authentication: JWT (ADMIN)

Headers:
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| limit | integer | No | Default 100 |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "captains": [
    {
      "user_id": "65c7f7d0e9f1c3a1b2c3d4e8",
      "go_home_mode": true,
      "go_home_eta_s": 900,
      "go_home_distance_m": 6200
    }
  ]
}
```

Status Codes:
200 OK
401 Unauthorized

Error Cases:
Invalid or missing JWT

Notes:
Used for admin visibility of route-based dispatch.

Admin Captains
Endpoint: POST /api/v1/admin/captain/{captain_id}/verify/

Purpose:
Approve or reject captain verification.

Method: POST

Authentication: JWT (ADMIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| captain_id | string | Yes | Captain user id |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| is_verified | boolean | Yes | true or false |
| reason | string | No | Verification reason |

Example Request:
```json
{
  "is_verified": true,
  "reason": "Documents verified"
}
```

Example Response:
```json
{
  "captain": {
    "user_id": "65c7f7d0e9f1c3a1b2c3d4e8",
    "is_verified": true,
    "verified_at": "2026-02-10T11:05:00.000Z"
  }
}
```

Status Codes:
200 OK
401 Unauthorized
404 Not Found

Error Cases:
Captain not found

Notes:
Rejecting a captain sets is_online to false.

Admin Recommendations
Endpoint: GET /api/v1/admin/recommendations/

Purpose:
List admin recommendations (legacy feed).

Method: GET

Authentication: JWT (ADMIN)

Headers:
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "recommendations": [
    {"_id": "65c7fb2de9f1c3a1b2c3d4f0", "type": "RESTAURANT", "title": "Top Rated"}
  ]
}
```

Status Codes:
200 OK
401 Unauthorized

Error Cases:
Invalid or missing JWT

Notes:
Legacy recommendations feed.

Admin Recommendations
Endpoint: POST /api/v1/admin/recommendations/

Purpose:
Create a legacy recommendation entry.

Method: POST

Authentication: JWT (ADMIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| type | string | Yes | RESTAURANT or MENU_ITEM |
| reference_id | string | Yes | Restaurant or menu item id |
| title | string | Yes | Title |
| description | string | Yes | Description |

Example Request:
```json
{
  "type": "RESTAURANT",
  "reference_id": "65c7f7fbe9f1c3a1b2c3d4e7",
  "title": "Top Rated",
  "description": "Chef specials"
}
```

Example Response:
```json
{
  "recommendation": {
    "_id": "65c80f18e9f1c3a1b2c3d4fc",
    "type": "RESTAURANT",
    "reference_id": "65c7f7fbe9f1c3a1b2c3d4e7",
    "title": "Top Rated"
  }
}
```

Status Codes:
201 Created
400 Bad Request
401 Unauthorized

Error Cases:
Invalid reference id

Notes:
These are separate from `is_recommended` flags on restaurants/menu items.

Admin Recommendations
Endpoint: DELETE /api/v1/admin/recommendations/{recommendation_id}/

Purpose:
Delete a legacy recommendation entry.

Method: DELETE

Authentication: JWT (ADMIN)

Headers:
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| recommendation_id | string | Yes | Recommendation id |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "deleted": true
}
```

Status Codes:
200 OK
400 Bad Request
401 Unauthorized
404 Not Found

Error Cases:
Recommendation not found

Notes:
Soft delete is not used; entry is removed.

Admin Recommendations
Endpoint: POST /api/v1/admin/recommend/restaurant

Purpose:
Mark/unmark a restaurant as recommended.

Method: POST

Authentication: JWT (ADMIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| restaurant_id | string | Yes | Restaurant id |
| is_recommended | boolean | No | Default true |

Example Request:
```json
{
  "restaurant_id": "65c7f7fbe9f1c3a1b2c3d4e7",
  "is_recommended": true
}
```

Example Response:
```json
{
  "restaurant": {
    "_id": "65c7f7fbe9f1c3a1b2c3d4e7",
    "is_recommended": true
  }
}
```

Status Codes:
200 OK
401 Unauthorized
404 Not Found

Error Cases:
Restaurant not found

Notes:
Recommended restaurants earn reward points for users.

Admin Recommendations
Endpoint: POST /api/v1/admin/recommend/menu

Purpose:
Mark/unmark a menu item as recommended.

Method: POST

Authentication: JWT (ADMIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| menu_item_id | string | Yes | Menu item id |
| is_recommended | boolean | No | Default true |

Example Request:
```json
{
  "menu_item_id": "65c7f8a7e9f1c3a1b2c3d4e6",
  "is_recommended": true
}
```

Example Response:
```json
{
  "menu_item": {
    "_id": "65c7f8a7e9f1c3a1b2c3d4e6",
    "is_recommended": true
  }
}
```

Status Codes:
200 OK
401 Unauthorized
404 Not Found

Error Cases:
Menu item not found

Notes:
Recommended menu items earn reward points for users.

Notifications
Endpoint: POST /api/v1/notify/send

Purpose:
Queue an immediate push notification.

Method: POST

Authentication: JWT (ADMIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| user_id | string | No | Target user id |
| topic | string | No | FCM topic name |
| title | string | Yes | Notification title |
| body | string | No | Notification body |
| data | object | No | Custom payload |
| priority | string | No | LOW, NORMAL, HIGH |
| silent | boolean | No | Default false |

Example Request:
```json
{
  "user_id": "65c7f7d0e9f1c3a1b2c3d4e5",
  "title": "Order placed",
  "body": "Your order is being prepared",
  "data": {"order_id": "65c809d9e9f1c3a1b2c3d4f9"},
  "priority": "HIGH"
}
```

Example Response:
```json
{
  "notification": {
    "_id": "65c8116ee9f1c3a1b2c3d4fd",
    "status": "QUEUED",
    "retry_count": 0
  }
}
```

Status Codes:
202 Accepted
400 Bad Request
401 Unauthorized

Error Cases:
Invalid payload

Notes:
Notifications are queued via Redis with retry logic.

Notifications
Endpoint: POST /api/v1/notify/schedule

Purpose:
Schedule a notification for future delivery.

Method: POST

Authentication: JWT (ADMIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| user_id | string | No | Target user id |
| topic | string | No | FCM topic name |
| title | string | Yes | Notification title |
| body | string | No | Notification body |
| data | object | No | Custom payload |
| priority | string | No | LOW, NORMAL, HIGH |
| silent | boolean | No | Default false |
| send_at | string | Yes | ISO 8601 datetime |

Example Request:
```json
{
  "user_id": "65c7f7d0e9f1c3a1b2c3d4e5",
  "title": "Promo",
  "body": "Discount available",
  "send_at": "2026-02-10T12:00:00Z"
}
```

Example Response:
```json
{
  "notification": {
    "_id": "65c81256e9f1c3a1b2c3d4fe",
    "status": "SCHEDULED",
    "send_at": "2026-02-10T12:00:00Z"
  }
}
```

Status Codes:
201 Created
400 Bad Request
401 Unauthorized

Error Cases:
Invalid send_at format

Notes:
Scheduled notifications are moved to the queue when send_at is reached.

Notifications
Endpoint: GET /api/v1/notify/history

Purpose:
List notification history.

Method: GET

Authentication: JWT (ADMIN)

Headers:
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| limit | integer | No | Default 50 |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "notifications": [
    {"_id": "65c8116ee9f1c3a1b2c3d4fd", "status": "SENT", "title": "Order placed"}
  ]
}
```

Status Codes:
200 OK
401 Unauthorized

Error Cases:
Invalid or missing JWT

Notes:
Includes queued, scheduled, sent, and failed notifications.

Fraud
Endpoint: GET /api/v1/fraud/scan/

Purpose:
Run fraud scan and return suspicious users.

Method: GET

Authentication: JWT (ADMIN)

Headers:
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| limit | integer | No | Default 200 |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "suspicious": [
    {
      "user_id": "65c7f7d0e9f1c3a1b2c3d4e5",
      "score": -0.42,
      "features": {"wallet_credit": 200000, "ride_count": 2}
    }
  ]
}
```

Status Codes:
200 OK
401 Unauthorized

Error Cases:
Invalid or missing JWT

Notes:
Uses anomaly detection over wallet and usage features.

Trust & Safety
Endpoint: GET /api/v1/trust/scan

Purpose:
Run trust scan for a user/device set.

Method: GET

Authentication: JWT (ADMIN)

Headers:
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| user_id | string | No | Filter by user id |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{}
```

Example Response:
```json
{
  "findings": [
    {"device_id": "device-123", "type": "DUPLICATE_DEVICE", "users": ["65c7f7d0e9f1c3a1b2c3d4e5"]}
  ],
  "device_count": 10
}
```

Status Codes:
200 OK
401 Unauthorized

Error Cases:
Invalid or missing JWT

Notes:
Detects duplicate devices and spoofing indicators.

Vehicle Rules
Endpoint: POST /api/v1/vehicle/rules

Purpose:
Update vehicle rules (admin-configurable).

Method: POST

Authentication: JWT (ADMIN)

Headers:
Content-Type: application/json
Authorization: Bearer <jwt>

Path Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| food_allowed_vehicles | array<string> | No | Default BIKE_PETROL, BIKE_EV |
| ev_reward_percentage | number | No | Example 0.10 for 10% |
| ev_bonus_multiplier | number | No | Multiplier for EV rewards |

Example Request:
```json
{
  "food_allowed_vehicles": ["BIKE_PETROL", "BIKE_EV"],
  "ev_reward_percentage": 0.1,
  "ev_bonus_multiplier": 1.2
}
```

Example Response:
```json
{
  "rules": {
    "food_allowed_vehicles": ["BIKE_PETROL", "BIKE_EV"],
    "ev_reward_percentage": 0.1,
    "ev_bonus_multiplier": 1.2
  }
}
```

Status Codes:
200 OK
401 Unauthorized
403 Forbidden

Error Cases:
Not allowed (non-admin)

Notes:
Rules are applied by matching and rewards engines.

**WebSocket APIs**
WebSocket
Endpoint: WS /ws/captain/{captain_id}/

Purpose:
Real-time job offers and status updates for captains.

Method: WS

Authentication: None (secured at gateway; JWT not enforced in WS layer)

Headers:
None

Path Params:
| Param | Type | Required | Notes |
| captain_id | string | Yes | Captain user id |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{"type": "ping"}
```

Example Response:
```json
{"type": "pong"}
```

Status Codes:
101 Switching Protocols

Error Cases:
Invalid room id

Notes:
Events: `job_offer`, `job_assigned`, `job_status`. Job offers include `go_home_job` when applicable.

WebSocket
Endpoint: WS /ws/user/{user_id}/

Purpose:
Real-time updates for users (job assigned, status, location).

Method: WS

Authentication: None (secured at gateway; JWT not enforced in WS layer)

Headers:
None

Path Params:
| Param | Type | Required | Notes |
| user_id | string | Yes | User id |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{"type": "ping"}
```

Example Response:
```json
{"type": "pong"}
```

Status Codes:
101 Switching Protocols

Error Cases:
Invalid room id

Notes:
Events: `job_assigned`, `job_status`, `location_update`.

WebSocket
Endpoint: WS /ws/order/{order_id}/

Purpose:
Order tracking updates (captain location).

Method: WS

Authentication: None (secured at gateway; JWT not enforced in WS layer)

Headers:
None

Path Params:
| Param | Type | Required | Notes |
| order_id | string | Yes | Order id |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{"type": "ping"}
```

Example Response:
```json
{"type": "pong"}
```

Status Codes:
101 Switching Protocols

Error Cases:
Invalid room id

Notes:
Event: `location_update` with captain coordinates.

WebSocket
Endpoint: WS /ws/chat/{room_id}/

Purpose:
Real-time chat between users, captains, and restaurants.

Method: WS

Authentication: None (secured at gateway; JWT not enforced in WS layer)

Headers:
None

Path Params:
| Param | Type | Required | Notes |
| room_id | string | Yes | Chat room id |

Query Params:
| Param | Type | Required | Notes |
| - | - | - | - |

Request Body:
| Field | Type | Required | Notes |
| - | - | - | - |

Example Request:
```json
{
  "type": "message",
  "sender_id": "65c7f7d0e9f1c3a1b2c3d4e5",
  "sender_role": "USER",
  "receiver_id": "65c7f7d0e9f1c3a1b2c3d4e8",
  "receiver_role": "CAPTAIN",
  "message": "On my way",
  "client_message_id": "msg_123"
}
```

Example Response:
```json
{
  "type": "ack",
  "message_id": "65c80544e9f1c3a1b2c3d4f4"
}
```

Status Codes:
101 Switching Protocols

Error Cases:
Invalid message payload

Notes:
Supports `message`, `delivered`, and `ping` types. Messages are broadcast to the room.

