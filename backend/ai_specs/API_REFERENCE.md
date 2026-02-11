# API Reference

Base URL: `/api/v1/`
Legacy base: `/api/` also routes all endpoints from `maps.urls` and `captains.urls` (same path after the base).
Authentication: JWT via `Authorization: Bearer <jwt>` unless stated otherwise.
Roles: USER, CAPTAIN, RESTAURANT, ADMIN.
Responses are JSON unless noted (Prometheus metrics are plain text).
Optional idempotency: `Idempotency-Key` header is honored for POST requests and replays successful responses.

## Public APIs

### Auth: Firebase Login
Endpoint: `POST /api/v1/auth/firebase/`
Purpose: Exchange a Firebase ID token for platform JWTs, creating the user if needed. The provided role is applied when the user has no role yet.
Authentication: None
Roles: None
Required Headers: `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| id_token | string | Yes | Firebase ID token |
| role | string | No | USER, CAPTAIN, RESTAURANT, ADMIN |
| device_id | string | No | Device identifier (or `X-Device-Id` header) |
| device_name | string | No | Device name (or `X-Device-Name` header) |

Example JSON Request:
```json
{
  "id_token": "<firebase_id_token>",
  "role": "USER",
  "device_id": "device-123"
}
```

Example JSON Response:
```json
{
  "token": "<access_jwt>",
  "refresh_token": "<refresh_jwt>",
  "user": {
    "_id": "<user_id>",
    "phone": "<phone_number>",
    "role": "USER"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Phone number not found in token"} |
| 400 | {"id_token": ["This field is required."]} |

### Auth: Refresh Token
Endpoint: `POST /api/v1/auth/refresh`
Purpose: Rotate a refresh token and issue a new access token.
Authentication: None
Roles: None
Required Headers: `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| refresh_token | string | Yes | Refresh JWT |

Example JSON Request:
```json
{
  "refresh_token": "<refresh_jwt>"
}
```

Example JSON Response:
```json
{
  "token": "<access_jwt>",
  "refresh_token": "<new_refresh_jwt>"
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 401 | {"detail": "Refresh token revoked"} |
| 401 | {"detail": "Session revoked"} |
| 404 | {"detail": "User not found"} |

### Restaurants: Menu List
Endpoint: `GET /api/v1/restaurants/<restaurant_id>/menu/list/`
Purpose: List menu items for a restaurant.
Authentication: None
Roles: None
Required Headers: None

Path Params:
| Name | Type | Description |
| --- | --- | --- |
| restaurant_id | string | Restaurant identifier |

Query Params: None.
Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "items": [
    {
      "_id": "<menu_item_id>",
      "name": "Chicken Biryani",
      "price": 25000,
      "is_available": true
    }
  ]
}
```

Possible Errors: None (returns empty list when no items match).

### Restaurants: Recommended
Endpoint: `GET /api/v1/restaurants/recommended/`
Purpose: List recommended restaurants.
Authentication: None
Roles: None
Required Headers: None

Path Params: None.

Query Params:
| Name | Type | Description |
| --- | --- | --- |
| limit | integer | Optional. Default 50. |

Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "restaurants": [
    {
      "_id": "<restaurant_id>",
      "name": "Biryani House",
      "is_recommended": true
    }
  ]
}
```

Possible Errors: None.

### Menu: Recommended Items
Endpoint: `GET /api/v1/menu/recommended/`
Purpose: List recommended menu items across restaurants.
Authentication: None
Roles: None
Required Headers: None

Path Params: None.

Query Params:
| Name | Type | Description |
| --- | --- | --- |
| limit | integer | Optional. Default 50. |

Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "items": [
    {
      "_id": "<menu_item_id>",
      "name": "Paneer Tikka",
      "price": 18000,
      "is_recommended": true
    }
  ]
}
```

Possible Errors: None.

### Recommendations: Public Feed
Endpoint: `GET /api/v1/recommendations/`
Purpose: List legacy recommendation entries visible to all users.
Authentication: None
Roles: None
Required Headers: None

Path Params: None.
Query Params: None.
Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "recommendations": [
    {
      "_id": "<recommendation_id>",
      "type": "RESTAURANT",
      "reference_id": "<restaurant_id>",
      "title": "Top Rated",
      "description": "Chef specials"
    }
  ]
}
```

Possible Errors: None.

## Shared Authenticated APIs

### Auth: Logout
Endpoint: `POST /api/v1/auth/logout`
Purpose: Revoke the current access token and optionally revoke the refresh token.
Authentication: JWT
Roles: Any authenticated
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| refresh_token | string | No | Refresh JWT to revoke |

Example JSON Request:
```json
{
  "refresh_token": "<refresh_jwt>"
}
```

Example JSON Response:
```json
{
  "success": true
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 401 | {"detail": "Invalid token"} |

### Users: Get Current User
Endpoint: `GET /api/v1/users/me/`
Purpose: Fetch the authenticated user's profile document.
Authentication: JWT
Roles: Any authenticated
Required Headers: `Authorization: Bearer <jwt>`

Path Params: None.
Query Params: None.
Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "user": {
    "_id": "<user_id>",
    "phone": "<phone_number>",
    "role": "USER"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Users: Register FCM Token
Endpoint: `POST /api/v1/users/fcm-token/`
Purpose: Register or update an FCM token for push notifications.
Authentication: JWT
Roles: Any authenticated
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| fcm_token | string | Yes | Device FCM token |

Example JSON Request:
```json
{
  "fcm_token": "<fcm_token>"
}
```

Example JSON Response:
```json
{
  "user": {
    "_id": "<user_id>",
    "fcm_token": "<fcm_token>"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"fcm_token": ["This field is required."]} |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Users: List Sessions
Endpoint: `GET /api/v1/users/sessions`
Purpose: List active refresh sessions for the authenticated user.
Authentication: JWT
Roles: Any authenticated
Required Headers: `Authorization: Bearer <jwt>`

Path Params: None.
Query Params: None.
Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "sessions": [
    {
      "device_id": "device-123",
      "device_name": "Pixel 7",
      "ip_address": "203.0.113.1"
    }
  ]
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Cancellation: Policy
Endpoint: `GET /api/v1/cancel/policy`
Purpose: Retrieve the current cancellation policy configuration.
Authentication: JWT
Roles: Any authenticated
Required Headers: `Authorization: Bearer <jwt>`

Path Params: None.
Query Params: None.
Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "policy": {
    "window_min": 5,
    "fee_pct": 0.1
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Payments: Razorpay Create Order
Endpoint: `POST /api/v1/payments/razorpay/order/`
Purpose: Create a Razorpay order for a payment amount.
Authentication: JWT
Roles: Any authenticated
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| amount | integer | Yes | Amount in smallest currency unit |
| currency | string | No | Default `INR` |
| receipt | string | Yes | Receipt reference |

Example JSON Request:
```json
{
  "amount": 15000,
  "currency": "INR",
  "receipt": "order_123"
}
```

Example JSON Response:
```json
{
  "razorpay_order": {
    "id": "order_abc123",
    "amount": 15000,
    "currency": "INR",
    "receipt": "order_123"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Invalid amount"} |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Payments: Razorpay Verify
Endpoint: `POST /api/v1/payments/razorpay/verify/`
Purpose: Verify a Razorpay payment signature.
Authentication: JWT
Roles: Any authenticated
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| razorpay_order_id | string | Yes | Razorpay order id |
| razorpay_payment_id | string | Yes | Razorpay payment id |
| razorpay_signature | string | Yes | Razorpay signature |

Example JSON Request:
```json
{
  "razorpay_order_id": "order_abc123",
  "razorpay_payment_id": "pay_123",
  "razorpay_signature": "sig_xyz"
}
```

Example JSON Response:
```json
{
  "verified": true
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Signature verification failed"} |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Pricing: Calculate Surge
Endpoint: `POST /api/v1/pricing/calculate/`
Purpose: Calculate surge multiplier for a location and job type.
Authentication: JWT
Roles: USER, CAPTAIN, RESTAURANT, ADMIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| job_type | string | Yes | `ORDER` or `RIDE` |
| lat | number | Yes | Latitude |
| lng | number | Yes | Longitude |

Example JSON Request:
```json
{
  "job_type": "RIDE",
  "lat": 12.9716,
  "lng": 77.5946
}
```

Example JSON Response:
```json
{
  "surge": {
    "surge_multiplier": 1.2,
    "demand": 5,
    "supply": 12,
    "ratio": 0.42
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Invalid job_type"} |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Maps: Route
Endpoint: `POST /api/v1/maps/route`
Purpose: Get route details between two points.
Authentication: JWT
Roles: USER, CAPTAIN, RESTAURANT, ADMIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`
Aliases: `/api/maps/route`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| origin_lat | number | Yes | Latitude |
| origin_lng | number | Yes | Longitude |
| destination_lat | number | Yes | Latitude |
| destination_lng | number | Yes | Longitude |
| mode | string | No | Default `driving` |

Example JSON Request:
```json
{
  "origin_lat": 12.9716,
  "origin_lng": 77.5946,
  "destination_lat": 12.9352,
  "destination_lng": 77.6245,
  "mode": "driving"
}
```

Example JSON Response:
```json
{
  "route": {
    "distance_m": 5200,
    "duration_s": 960,
    "polyline": "<encoded_polyline>"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Google Maps error"} |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Maps: ETA
Endpoint: `POST /api/v1/maps/eta`
Purpose: Get ETA details between two points.
Authentication: JWT
Roles: USER, CAPTAIN, RESTAURANT, ADMIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`
Aliases: `/api/maps/eta`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| origin_lat | number | Yes | Latitude |
| origin_lng | number | Yes | Longitude |
| destination_lat | number | Yes | Latitude |
| destination_lng | number | Yes | Longitude |
| mode | string | No | Default `driving` |

Example JSON Request:
```json
{
  "origin_lat": 12.9716,
  "origin_lng": 77.5946,
  "destination_lat": 12.9352,
  "destination_lng": 77.6245
}
```

Example JSON Response:
```json
{
  "eta": {
    "distance_m": 5200,
    "duration_s": 900,
    "duration_in_traffic_s": 1050
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Google Maps error"} |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Maps: Nearby Captains
Endpoint: `GET /api/v1/captain/nearby`
Purpose: Find nearby captains for a location.
Authentication: JWT
Roles: USER, ADMIN
Required Headers: `Authorization: Bearer <jwt>`
Aliases: `/api/captain/nearby`

Path Params: None.

Query Params:
| Name | Type | Description |
| --- | --- | --- |
| lat | number | Latitude |
| lng | number | Longitude |
| radius_m | integer | Optional. Default 5000 (min 100, max 20000). |

Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "captains": [
    {
      "_id": "<captain_id>",
      "vehicle_type": "BIKE",
      "is_online": true
    }
  ]
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Invalid coordinates"} |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Routing: Optimize Route
Endpoint: `POST /api/v1/route/optimize/`
Purpose: Optimize the order of multiple points for routing.
Authentication: JWT
Roles: USER, CAPTAIN, RESTAURANT, ADMIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| points | array<object> | Yes | Array of `{lat, lng}` |
| clusters | integer | No | 1 to 10 |

Example JSON Request:
```json
{
  "points": [
    {"lat": 12.97, "lng": 77.59},
    {"lat": 12.95, "lng": 77.6}
  ],
  "clusters": 2
}
```

Example JSON Response:
```json
{
  "optimized": [
    {"lat": 12.97, "lng": 77.59},
    {"lat": 12.95, "lng": 77.6}
  ]
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"points": ["This field is required."]} |
| 401 | {"detail": "Authentication credentials were not provided"} |

### ETA: Predict
Endpoint: `POST /api/v1/eta/predict`
Purpose: Predict ETA with prep time and traffic/weather factors.
Authentication: JWT
Roles: USER, CAPTAIN, RESTAURANT, ADMIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| origin_lat | number | Yes | Latitude |
| origin_lng | number | Yes | Longitude |
| destination_lat | number | Yes | Latitude |
| destination_lng | number | Yes | Longitude |
| prep_time_min | integer | No | Default 0 |
| batch_size | integer | No | Default 1 |
| traffic_factor | number | No | Default 1.0 |
| weather_factor | number | No | Default 1.0 |

Example JSON Request:
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

Example JSON Response:
```json
{
  "eta": {
    "duration_s": 1200,
    "prep_time_min": 15
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"origin_lat": ["This field is required."]} |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Campaigns: Active
Endpoint: `GET /api/v1/campaigns/active`
Purpose: List active promotions or campaigns.
Authentication: JWT
Roles: Any authenticated
Required Headers: `Authorization: Bearer <jwt>`

Path Params: None.

Query Params:
| Name | Type | Description |
| --- | --- | --- |
| limit | integer | Optional. Default 50. |

Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "campaigns": [
    {
      "_id": "<campaign_id>",
      "title": "Festival Promo"
    }
  ]
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Vehicles: Rules (Read)
Endpoint: `GET /api/v1/vehicle/rules`
Purpose: Fetch vehicle rules used by matching and rewards logic.
Authentication: JWT
Roles: Any authenticated
Required Headers: `Authorization: Bearer <jwt>`

Path Params: None.
Query Params: None.
Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "rules": {
    "food_allowed_vehicles": ["BIKE_PETROL", "BIKE_EV"],
    "ev_reward_percentage": 0.1,
    "ev_bonus_multiplier": 1.0
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Support: Create Ticket
Endpoint: `POST /api/v1/support/ticket`
Purpose: Create a support ticket.
Authentication: JWT
Roles: USER, CAPTAIN, RESTAURANT
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| subject | string | Yes | Ticket subject |
| message | string | Yes | Ticket message |
| category | string | No | Category label |
| priority | string | No | LOW, NORMAL, HIGH |

Example JSON Request:
```json
{
  "subject": "Refund issue",
  "message": "I was charged twice",
  "priority": "HIGH"
}
```

Example JSON Response:
```json
{
  "ticket": {
    "_id": "<ticket_id>",
    "subject": "Refund issue",
    "priority": "HIGH"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"subject": ["This field is required."]} |
| 401 | {"detail": "Authentication credentials were not provided"} |
| 403 | {"detail": "Role not allowed"} |

## Profile Management

### Users: Update Profile
Endpoint: `PATCH /api/v1/users/me/`
Purpose: Update editable fields on the USER profile.
Authentication: JWT
Roles: USER
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| name | string | No | Display name |
| email | string | No | Email address |
| avatar_url | string | No | Avatar URL |
| default_address | object | No | Free-form address object |
| preferences | object | No | Free-form preferences |

Example JSON Request:
```json
{
  "name": "Asha Rao",
  "email": "asha@example.com",
  "avatar_url": "https://cdn.example.com/u/asha.png",
  "preferences": {"language": "en"}
}
```

Example JSON Response:
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "_id": "<user_id>",
    "name": "Asha Rao",
    "email": "asha@example.com"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "No valid fields to update"} |
| 403 | {"detail": "Only USER can update this profile"} |
| 404 | {"detail": "User not found"} |

### Captains: Update Profile
Endpoint: `PATCH /api/v1/captain/me/`
Purpose: Update editable fields on the CAPTAIN profile.
Authentication: JWT
Roles: CAPTAIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| name | string | No | Display name |
| avatar_url | string | No | Avatar URL |
| vehicle_number | string | No | Vehicle number |
| vehicle_type | string | No | Vehicle type |
| home_location | object | No | `{lat, lng}` |
| bio | string | No | Short bio |

Example JSON Request:
```json
{
  "name": "Ravi Kumar",
  "vehicle_number": "KA01AB1234",
  "vehicle_type": "BIKE",
  "home_location": {"lat": 12.9716, "lng": 77.5946}
}
```

Example JSON Response:
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "user_id": "<user_id>",
    "name": "Ravi Kumar",
    "vehicle_type": "BIKE"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "No valid fields to update"} |
| 403 | {"detail": "Role not allowed"} |
| 404 | {"detail": "Captain not found"} |

### Restaurants: Update Profile
Endpoint: `PATCH /api/v1/restaurant/me/`
Purpose: Update editable fields on the RESTAURANT profile.
Authentication: JWT
Roles: RESTAURANT
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| name | string | No | Restaurant name |
| logo_url | string | No | Logo URL |
| address | string | No | Address |
| opening_time | string | No | Example `09:00` |
| closing_time | string | No | Example `23:00` |
| is_open | boolean | No | Open/closed flag |
| support_phone | string | No | Support phone (requires verification) |

Example JSON Request:
```json
{
  "name": "Biryani House",
  "address": "MG Road",
  "opening_time": "09:00",
  "closing_time": "23:00",
  "is_open": true
}
```

Example JSON Response:
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "_id": "<restaurant_id>",
    "name": "Biryani House",
    "is_open": true
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "No valid fields to update"} |
| 403 | {"detail": "support_phone can be updated only after verification"} |
| 404 | {"detail": "Restaurant not found"} |

## User APIs

### Addresses: Create
Endpoint: `POST /api/v1/users/address`
Purpose: Create a saved address for the authenticated user.
Authentication: JWT
Roles: USER
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| label | string | Yes | HOME, WORK, OTHER |
| line1 | string | Yes | Address line 1 |
| line2 | string | No | Address line 2 |
| city | string | No | City |
| state | string | No | State |
| postal_code | string | No | Postal code |
| landmark | string | No | Landmark |
| lat | number | No | Latitude (requires `lng`) |
| lng | number | No | Longitude (requires `lat`) |
| is_default | boolean | No | Default address flag |

Example JSON Request:
```json
{
  "label": "HOME",
  "line1": "MG Road",
  "city": "Bengaluru",
  "lat": 12.9716,
  "lng": 77.5946,
  "is_default": true
}
```

Example JSON Response:
```json
{
  "address": {
    "_id": "<address_id>",
    "label": "HOME",
    "line1": "MG Road",
    "city": "Bengaluru",
    "is_default": true
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "lat and lng must be provided together"} |
| 401 | {"detail": "Authentication credentials were not provided"} |
| 403 | {"detail": "Role not allowed"} |

### Addresses: List
Endpoint: `GET /api/v1/users/address`
Purpose: List saved addresses for the authenticated user.
Authentication: JWT
Roles: USER
Required Headers: `Authorization: Bearer <jwt>`

Path Params: None.
Query Params: None.
Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "addresses": [
    {
      "_id": "<address_id>",
      "label": "HOME",
      "line1": "MG Road"
    }
  ]
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 401 | {"detail": "Authentication credentials were not provided"} |
| 403 | {"detail": "Role not allowed"} |

### Addresses: Update
Endpoint: `PATCH /api/v1/users/address/<address_id>`
Purpose: Update a saved address.
Authentication: JWT
Roles: USER
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params:
| Name | Type | Description |
| --- | --- | --- |
| address_id | string | Address identifier |

Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| label | string | No | HOME, WORK, OTHER |
| line1 | string | No | Address line 1 |
| line2 | string | No | Address line 2 |
| city | string | No | City |
| state | string | No | State |
| postal_code | string | No | Postal code |
| landmark | string | No | Landmark |
| lat | number | No | Latitude (requires `lng`) |
| lng | number | No | Longitude (requires `lat`) |
| is_default | boolean | No | Default address flag |

Example JSON Request:
```json
{
  "label": "WORK",
  "is_default": false
}
```

Example JSON Response:
```json
{
  "address": {
    "_id": "<address_id>",
    "label": "WORK",
    "is_default": false
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "lat and lng must be provided together"} |
| 401 | {"detail": "Authentication credentials were not provided"} |
| 403 | {"detail": "Role not allowed"} |
| 404 | {"detail": "Address not found"} |

### Addresses: Delete
Endpoint: `DELETE /api/v1/users/address/<address_id>`
Purpose: Delete a saved address.
Authentication: JWT
Roles: USER
Required Headers: `Authorization: Bearer <jwt>`

Path Params:
| Name | Type | Description |
| --- | --- | --- |
| address_id | string | Address identifier |

Query Params: None.
Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "deleted": true
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 401 | {"detail": "Authentication credentials were not provided"} |
| 403 | {"detail": "Role not allowed"} |
| 404 | {"detail": "Address not found"} |

### Favorites: Create
Endpoint: `POST /api/v1/favorites`
Purpose: Add a restaurant or menu item to favorites.
Authentication: JWT
Roles: USER
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| favorite_type | string | Yes | RESTAURANT or MENU_ITEM |
| reference_id | string | Yes | ID of the target entity |

Example JSON Request:
```json
{
  "favorite_type": "RESTAURANT",
  "reference_id": "<restaurant_id>"
}
```

Example JSON Response:
```json
{
  "favorite": {
    "_id": "<favorite_id>",
    "favorite_type": "RESTAURANT",
    "reference_id": "<restaurant_id>"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"favorite_type": ["This field is required."]} |
| 401 | {"detail": "Authentication credentials were not provided"} |
| 403 | {"detail": "Role not allowed"} |

### Orders: Checkout
Endpoint: `POST /api/v1/orders/checkout/`
Purpose: Calculate order totals, surge, and reward effects before placing an order.
Authentication: JWT
Roles: USER
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| restaurant_id | string | Yes | Restaurant id |
| items | array<object> | Yes | Array of `{menu_item_id, quantity}` |
| redeem_points | integer | No | Reward points to redeem |

Example JSON Request:
```json
{
  "restaurant_id": "<restaurant_id>",
  "items": [
    {"menu_item_id": "<menu_item_id>", "quantity": 2}
  ],
  "redeem_points": 50
}
```

Example JSON Response:
```json
{
  "items": [
    {"menu_item_id": "<menu_item_id>", "name": "Biryani", "price": 25000, "quantity": 2, "total": 50000}
  ],
  "subtotal": 50000,
  "surge_multiplier": 1.0,
  "surge_amount": 0,
  "total_before_rewards": 50000,
  "redeem_points_applied": 50,
  "redeem_amount": 5000,
  "reward_points_earned": 10,
  "total": 45000
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Invalid restaurant id"} |
| 400 | {"detail": "Some menu items are unavailable"} |
| 401 | {"detail": "Authentication credentials were not provided"} |
| 403 | {"detail": "Role not allowed"} |

### Orders: Create
Endpoint: `POST /api/v1/orders/`
Purpose: Create a food order and optionally create a Razorpay order for payment.
Authentication: JWT
Roles: USER
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| restaurant_id | string | Yes | Restaurant id |
| items | array<object> | Yes | Array of `{menu_item_id, quantity}` |
| payment_mode | string | Yes | RAZORPAY, COD, WALLET, WALLET_RAZORPAY |
| wallet_amount | integer | No | Wallet amount to use |
| redeem_points | integer | No | Reward points to redeem |

Example JSON Request:
```json
{
  "restaurant_id": "<restaurant_id>",
  "items": [
    {"menu_item_id": "<menu_item_id>", "quantity": 2}
  ],
  "payment_mode": "WALLET_RAZORPAY",
  "wallet_amount": 5000,
  "redeem_points": 50
}
```

Example JSON Response:
```json
{
  "order": {
    "_id": "<order_id>",
    "status": "PENDING_PAYMENT",
    "amount_total": 45000,
    "payment_mode": "WALLET_RAZORPAY"
  },
  "items": [
    {"menu_item_id": "<menu_item_id>", "name": "Biryani", "price": 25000, "quantity": 2, "total": 50000}
  ],
  "razorpay_order": {
    "id": "order_abc123",
    "amount": 40000,
    "currency": "INR"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Invalid payment mode"} |
| 400 | {"detail": "Insufficient wallet balance"} |
| 401 | {"detail": "Authentication credentials were not provided"} |
| 403 | {"detail": "Role not allowed"} |

### Orders: Verify Payment
Endpoint: `POST /api/v1/orders/verify-payment/`
Purpose: Verify Razorpay payment and mark the order as paid.
Authentication: JWT
Roles: USER
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| order_id | string | Yes | Order id |
| razorpay_order_id | string | Yes | Razorpay order id |
| razorpay_payment_id | string | Yes | Razorpay payment id |
| razorpay_signature | string | Yes | Razorpay signature |

Example JSON Request:
```json
{
  "order_id": "<order_id>",
  "razorpay_order_id": "order_abc123",
  "razorpay_payment_id": "pay_123",
  "razorpay_signature": "sig_xyz"
}
```

Example JSON Response:
```json
{
  "order": {
    "_id": "<order_id>",
    "is_paid": true,
    "status": "PLACED"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Invalid order id"} |
| 400 | {"detail": "Order not found"} |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Orders: Reorder
Endpoint: `POST /api/v1/orders/reorder/<order_id>`
Purpose: Create a new order based on a previous order.
Authentication: JWT
Roles: USER
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params:
| Name | Type | Description |
| --- | --- | --- |
| order_id | string | Previous order id |

Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| payment_mode | string | Yes | RAZORPAY, COD, WALLET, WALLET_RAZORPAY |
| wallet_amount | integer | No | Wallet amount to use |
| redeem_points | integer | No | Reward points to redeem |

Example JSON Request:
```json
{
  "payment_mode": "WALLET_RAZORPAY",
  "wallet_amount": 2000,
  "redeem_points": 20
}
```

Example JSON Response:
```json
{
  "order": {
    "_id": "<order_id>",
    "status": "PENDING_PAYMENT"
  },
  "items": [
    {"menu_item_id": "<menu_item_id>", "quantity": 2}
  ],
  "razorpay_order": {
    "id": "order_abc123",
    "amount": 30000,
    "currency": "INR"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Order not found"} |
| 400 | {"detail": "Order items not found"} |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Rides: Fare Estimate
Endpoint: `POST /api/v1/rides/fare/`
Purpose: Calculate fare estimate for a ride.
Authentication: JWT
Roles: USER
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| pickup_lat | number | Yes | Pickup latitude |
| pickup_lng | number | Yes | Pickup longitude |
| dropoff_lat | number | Yes | Dropoff latitude |
| dropoff_lng | number | Yes | Dropoff longitude |
| vehicle_type | string | Yes | Vehicle type |

Example JSON Request:
```json
{
  "pickup_lat": 12.9716,
  "pickup_lng": 77.5946,
  "dropoff_lat": 12.9352,
  "dropoff_lng": 77.6245,
  "vehicle_type": "BIKE"
}
```

Example JSON Response:
```json
{
  "fare_base": 120,
  "surge_multiplier": 1.0,
  "surge_amount": 0,
  "fare_total": 120,
  "reward_points_preview": 0
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Invalid vehicle_type. Allowed: BIKE_PETROL, BIKE_EV, AUTO, CAR, SUV"} |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Rides: Create
Endpoint: `POST /api/v1/rides/`
Purpose: Create a ride and optionally create a Razorpay order for payment.
Authentication: JWT
Roles: USER
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| pickup_lat | number | Yes | Pickup latitude |
| pickup_lng | number | Yes | Pickup longitude |
| dropoff_lat | number | Yes | Dropoff latitude |
| dropoff_lng | number | Yes | Dropoff longitude |
| vehicle_type | string | Yes | Vehicle type |
| payment_mode | string | Yes | RAZORPAY, WALLET, WALLET_RAZORPAY |
| wallet_amount | integer | No | Wallet amount to use |
| redeem_points | integer | No | Reward points to redeem |

Example JSON Request:
```json
{
  "pickup_lat": 12.9716,
  "pickup_lng": 77.5946,
  "dropoff_lat": 12.9352,
  "dropoff_lng": 77.6245,
  "vehicle_type": "BIKE",
  "payment_mode": "WALLET_RAZORPAY",
  "wallet_amount": 2000,
  "redeem_points": 150
}
```

Example JSON Response:
```json
{
  "ride": {
    "_id": "<ride_id>",
    "status": "PENDING_PAYMENT",
    "fare": 180,
    "payment_mode": "WALLET_RAZORPAY"
  },
  "razorpay_order": {
    "id": "order_abc123",
    "amount": 160,
    "currency": "INR"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Invalid payment mode"} |
| 400 | {"detail": "Insufficient wallet balance"} |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Rides: Schedule
Endpoint: `POST /api/v1/rides/schedule`
Purpose: Schedule a ride for a future time.
Authentication: JWT
Roles: USER
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| pickup_lat | number | Yes | Pickup latitude |
| pickup_lng | number | Yes | Pickup longitude |
| dropoff_lat | number | Yes | Dropoff latitude |
| dropoff_lng | number | Yes | Dropoff longitude |
| vehicle_type | string | Yes | Vehicle type |
| scheduled_for | string | Yes | ISO 8601 datetime |
| payment_mode | string | No | RAZORPAY, WALLET, WALLET_RAZORPAY |
| wallet_amount | integer | No | Wallet amount to use |
| redeem_points | integer | No | Reward points to redeem |

Example JSON Request:
```json
{
  "pickup_lat": 12.9716,
  "pickup_lng": 77.5946,
  "dropoff_lat": 12.9352,
  "dropoff_lng": 77.6245,
  "vehicle_type": "BIKE",
  "scheduled_for": "2026-02-11T09:00:00Z"
}
```

Example JSON Response:
```json
{
  "ride": {
    "_id": "<ride_id>",
    "status": "SCHEDULED",
    "scheduled_for": "2026-02-11T09:00:00Z"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"scheduled_for": ["This field is required."]} |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Rides: Verify Payment
Endpoint: `POST /api/v1/rides/verify-payment/`
Purpose: Verify Razorpay payment and mark the ride as paid.
Authentication: JWT
Roles: USER
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| ride_id | string | Yes | Ride id |
| razorpay_order_id | string | Yes | Razorpay order id |
| razorpay_payment_id | string | Yes | Razorpay payment id |
| razorpay_signature | string | Yes | Razorpay signature |

Example JSON Request:
```json
{
  "ride_id": "<ride_id>",
  "razorpay_order_id": "order_abc123",
  "razorpay_payment_id": "pay_123",
  "razorpay_signature": "sig_xyz"
}
```

Example JSON Response:
```json
{
  "ride": {
    "_id": "<ride_id>",
    "is_paid": true,
    "status": "REQUESTED"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Invalid ride id"} |
| 400 | {"detail": "Ride not found"} |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Ratings: Rate Captain
Endpoint: `POST /api/v1/captain/rate/`
Purpose: Submit a rating and optional comment for a captain on a job.
Authentication: JWT
Roles: USER
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| job_type | string | Yes | ORDER or RIDE |
| job_id | string | Yes | Order or ride id |
| rating | integer | Yes | 1 to 5 |
| comment | string | No | Optional comment |

Example JSON Request:
```json
{
  "job_type": "RIDE",
  "job_id": "<ride_id>",
  "rating": 5,
  "comment": "Great ride"
}
```

Example JSON Response:
```json
{
  "rating": {
    "_id": "<rating_id>",
    "rating": 5,
    "comment": "Great ride"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Job not found"} |
| 400 | {"detail": "Rating already submitted for this job"} |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Promotions: Apply Coupon
Endpoint: `POST /api/v1/coupon/apply`
Purpose: Validate and apply a coupon for a given amount.
Authentication: JWT
Roles: USER
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| code | string | Yes | Coupon code |
| amount | integer | Yes | Order amount |
| job_type | string | Yes | ORDER or RIDE |

Example JSON Request:
```json
{
  "code": "WELCOME",
  "amount": 25000,
  "job_type": "ORDER"
}
```

Example JSON Response:
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

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Coupon not found"} |
| 400 | {"detail": "Coupon expired"} |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Promotions: Use Referral
Endpoint: `POST /api/v1/referral/use`
Purpose: Redeem a referral code.
Authentication: JWT
Roles: USER
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| referral_code | string | Yes | Referral code |

Example JSON Request:
```json
{
  "referral_code": "GORIDES123"
}
```

Example JSON Response:
```json
{
  "used": true
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Invalid referral code"} |
| 400 | {"detail": "Referral already used"} |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Growth: Personalized Feed
Endpoint: `GET /api/v1/feed/personalized`
Purpose: Return a personalized feed for the authenticated user.
Authentication: JWT
Roles: USER
Required Headers: `Authorization: Bearer <jwt>`

Path Params: None.

Query Params:
| Name | Type | Description |
| --- | --- | --- |
| limit | integer | Optional. Default 50. |

Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "feed": [
    {
      "_id": "<recommendation_id>",
      "type": "RESTAURANT",
      "title": "Top Rated"
    }
  ]
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 401 | {"detail": "Authentication credentials were not provided"} |
| 403 | {"detail": "Role not allowed"} |

### Growth: Experiment Assign
Endpoint: `POST /api/v1/experiment/assign`
Purpose: Deterministically assign a user to an experiment variant.
Authentication: JWT
Roles: USER, ADMIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| experiment_key | string | Yes | Experiment key |
| variants | array<string> | Yes | List of variants |

Example JSON Request:
```json
{
  "experiment_key": "homepage_v1",
  "variants": ["A", "B"]
}
```

Example JSON Response:
```json
{
  "assignment": {
    "experiment_key": "homepage_v1",
    "variant": "A"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "No variants provided"} |
| 401 | {"detail": "Authentication credentials were not provided"} |
| 403 | {"detail": "Role not allowed"} |

## Captain APIs

### Captain: Set Online Status
Endpoint: `POST /api/v1/captain/online/`
Purpose: Set the captain's online/offline status.
Authentication: JWT
Roles: CAPTAIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`
Aliases: `/api/v1/captains/online/`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| is_online | boolean | Yes | Online status |

Example JSON Request:
```json
{
  "is_online": true
}
```

Example JSON Response:
```json
{
  "captain": {
    "user_id": "<user_id>",
    "is_online": true
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 403 | {"detail": "Role not allowed"} |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Captain: Update Location
Endpoint: `POST /api/v1/captain/location/`
Purpose: Update the captain's current location.
Authentication: JWT
Roles: CAPTAIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`
Aliases: `/api/v1/captains/location/`, `/api/v1/captain/location/update`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| lat | number | Yes | Latitude |
| lng | number | Yes | Longitude |

Example JSON Request:
```json
{
  "lat": 12.9716,
  "lng": 77.5946
}
```

Example JSON Response:
```json
{
  "captain": {
    "user_id": "<user_id>",
    "location": {"type": "Point", "coordinates": [77.5946, 12.9716]}
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 403 | {"detail": "Role not allowed"} |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Captain: Register Vehicle (Captain Profile)
Endpoint: `POST /api/v1/captain/vehicle/register/`
Purpose: Register a vehicle for the captain and update captain profile.
Authentication: JWT
Roles: CAPTAIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| vehicle_type | string | Yes | Vehicle type |
| vehicle_number | string | Yes | Vehicle number |
| vehicle_brand | string | Yes | Vehicle brand |
| license_number | string | Yes | License number |
| rc_image | string | Yes | RC image URL |
| license_image | string | Yes | License image URL |

Example JSON Request:
```json
{
  "vehicle_type": "BIKE",
  "vehicle_number": "KA01AB1234",
  "vehicle_brand": "Honda",
  "license_number": "DL123456",
  "rc_image": "https://cdn.example.com/rc.jpg",
  "license_image": "https://cdn.example.com/license.jpg"
}
```

Example JSON Response:
```json
{
  "vehicle": {
    "_id": "<vehicle_id>",
    "vehicle_type": "BIKE_PETROL",
    "vehicle_number": "KA01AB1234"
  },
  "captain": {
    "user_id": "<user_id>",
    "vehicle_number": "KA01AB1234"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Invalid vehicle_type. Allowed: BIKE_PETROL, BIKE_EV, AUTO, CAR, SUV"} |
| 404 | {"detail": "Captain not found"} |

### Captain: Register Vehicle (Vehicles Service)
Endpoint: `POST /api/v1/vehicle/register`
Purpose: Register a vehicle for the captain (vehicles service endpoint).
Authentication: JWT
Roles: CAPTAIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| vehicle_type | string | Yes | Vehicle type |
| vehicle_number | string | Yes | Vehicle number |
| vehicle_brand | string | Yes | Vehicle brand |
| license_number | string | Yes | License number |
| rc_image | string | Yes | RC image URL |
| license_image | string | Yes | License image URL |

Example JSON Request:
```json
{
  "vehicle_type": "BIKE_EV",
  "vehicle_number": "KA01AB1234",
  "vehicle_brand": "Ather",
  "license_number": "DL123",
  "rc_image": "https://cdn.example.com/rc.jpg",
  "license_image": "https://cdn.example.com/license.jpg"
}
```

Example JSON Response:
```json
{
  "vehicle": {
    "_id": "<vehicle_id>",
    "vehicle_type": "BIKE_EV",
    "vehicle_number": "KA01AB1234"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 404 | {"detail": "Captain not found"} |
| 403 | {"detail": "Role not allowed"} |

### Captain: Get Vehicle
Endpoint: `GET /api/v1/captain/vehicle/me/`
Purpose: Fetch the captain's registered vehicle.
Authentication: JWT
Roles: CAPTAIN
Required Headers: `Authorization: Bearer <jwt>`

Path Params: None.
Query Params: None.
Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "vehicle": {
    "_id": "<vehicle_id>",
    "vehicle_type": "BIKE",
    "vehicle_number": "KA01AB1234"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 404 | {"detail": "Captain not found"} |
| 403 | {"detail": "Role not allowed"} |

### Captain: Enable Go-Home Mode
Endpoint: `POST /api/v1/captain/go-home/enable`
Purpose: Enable go-home mode with a destination location.
Authentication: JWT
Roles: CAPTAIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| lat | number | Yes | Latitude |
| lng | number | Yes | Longitude |

Example JSON Request:
```json
{
  "lat": 17.385044,
  "lng": 78.486671
}
```

Example JSON Response:
```json
{
  "captain": {
    "user_id": "<user_id>",
    "go_home": true
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 404 | {"detail": "Captain not found"} |
| 403 | {"detail": "Role not allowed"} |

### Captain: Disable Go-Home Mode
Endpoint: `POST /api/v1/captain/go-home/disable`
Purpose: Disable go-home mode.
Authentication: JWT
Roles: CAPTAIN
Required Headers: `Authorization: Bearer <jwt>`

Path Params: None.
Query Params: None.
Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "captain": {
    "user_id": "<user_id>",
    "go_home": false
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 404 | {"detail": "Captain not found"} |
| 403 | {"detail": "Role not allowed"} |

### Captain: Earnings
Endpoint: `GET /api/v1/captain/earnings`
Purpose: Fetch the captain's wallet/earnings summary.
Authentication: JWT
Roles: CAPTAIN
Required Headers: `Authorization: Bearer <jwt>`

Path Params: None.
Query Params: None.
Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "wallet": {
    "captain_id": "<captain_id>",
    "balance": 12000,
    "updated_at": "2026-02-11T00:00:00Z"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 403 | {"detail": "Role not allowed"} |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Captain: Request Payout
Endpoint: `POST /api/v1/captain/payout/request`
Purpose: Request a payout to the linked bank account.
Authentication: JWT
Roles: CAPTAIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| amount | integer | Yes | Payout amount |

Example JSON Request:
```json
{
  "amount": 5000
}
```

Example JSON Response:
```json
{
  "payout": {
    "_id": "<payout_id>",
    "amount": 5000,
    "tds_amount": 50,
    "net_amount": 4950,
    "status": "PENDING"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Insufficient balance"} |
| 403 | {"detail": "Role not allowed"} |

### Captain: Payout History
Endpoint: `GET /api/v1/captain/payout/history`
Purpose: List payout history for the captain.
Authentication: JWT
Roles: CAPTAIN
Required Headers: `Authorization: Bearer <jwt>`

Path Params: None.

Query Params:
| Name | Type | Description |
| --- | --- | --- |
| limit | integer | Optional. Default 50. |

Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "payouts": [
    {
      "_id": "<payout_id>",
      "amount": 5000,
      "status": "PAID"
    }
  ]
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 403 | {"detail": "Role not allowed"} |

### Captain: Link Bank Account
Endpoint: `POST /api/v1/captain/bank/link`
Purpose: Link a bank account for payouts.
Authentication: JWT
Roles: CAPTAIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| account_number | string | Yes | Bank account number |
| ifsc | string | Yes | IFSC code |
| name | string | Yes | Account holder name |
| upi | string | No | UPI id |

Example JSON Request:
```json
{
  "account_number": "1234567890",
  "ifsc": "HDFC0001234",
  "name": "Captain",
  "upi": "captain@upi"
}
```

Example JSON Response:
```json
{
  "bank_account": {
    "_id": "<bank_id>",
    "ifsc": "HDFC0001234",
    "account_number": "1234567890"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Invalid captain"} |
| 403 | {"detail": "Role not allowed"} |

### Captain: Complete Ride
Endpoint: `POST /api/v1/rides/complete/`
Purpose: Mark a ride as completed.
Authentication: JWT
Roles: CAPTAIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| ride_id | string | Yes | Ride id |

Example JSON Request:
```json
{
  "ride_id": "<ride_id>"
}
```

Example JSON Response:
```json
{
  "ride": {
    "_id": "<ride_id>",
    "status": "COMPLETED"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 404 | {"detail": "Ride not found"} |
| 403 | {"detail": "Role not allowed"} |

### Captain: Stats
Endpoint: `GET /api/v1/captain/<captain_id>/stats/`
Purpose: Retrieve aggregate stats for a captain.
Authentication: JWT
Roles: Any authenticated
Required Headers: `Authorization: Bearer <jwt>`

Path Params:
| Name | Type | Description |
| --- | --- | --- |
| captain_id | string | Captain identifier |

Query Params: None.
Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "stats": {
    "captain_id": "<captain_id>",
    "average_rating": 4.8,
    "total_ratings": 120,
    "total_trips": 300,
    "cancellation_rate": 0.02
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 404 | {"detail": "Captain not found"} |
| 401 | {"detail": "Authentication credentials were not provided"} |

## Restaurant APIs

### Restaurants: Create
Endpoint: `POST /api/v1/restaurants/`
Purpose: Create a restaurant profile for the authenticated owner.
Authentication: JWT
Roles: RESTAURANT
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| name | string | Yes | Restaurant name |
| address | string | No | Address |
| phone | string | No | Phone number |
| lat | number | No | Latitude |
| lng | number | No | Longitude |

Example JSON Request:
```json
{
  "name": "Biryani House",
  "address": "MG Road",
  "phone": "+919999999999",
  "lat": 12.97,
  "lng": 77.59
}
```

Example JSON Response:
```json
{
  "restaurant": {
    "_id": "<restaurant_id>",
    "name": "Biryani House",
    "address": "MG Road"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 403 | {"detail": "Role not allowed"} |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Restaurants: Add Menu Item
Endpoint: `POST /api/v1/restaurants/<restaurant_id>/menu/`
Purpose: Add a menu item to a restaurant.
Authentication: JWT
Roles: RESTAURANT
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params:
| Name | Type | Description |
| --- | --- | --- |
| restaurant_id | string | Restaurant identifier |

Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| name | string | Yes | Menu item name |
| price | integer | Yes | Price in smallest currency unit |
| is_available | boolean | No | Default true |

Example JSON Request:
```json
{
  "name": "Chicken Biryani",
  "price": 25000,
  "is_available": true
}
```

Example JSON Response:
```json
{
  "menu_item": {
    "_id": "<menu_item_id>",
    "name": "Chicken Biryani",
    "price": 25000,
    "is_available": true
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 403 | {"detail": "Not allowed"} |
| 404 | {"detail": "Restaurant not found"} |

### Restaurant Ops: Update Order Status
Endpoint: `POST /api/v1/restaurant/order/update`
Purpose: Update the status of a restaurant order.
Authentication: JWT
Roles: RESTAURANT
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| order_id | string | Yes | Order id |
| status | string | Yes | New status |
| prep_time_min | integer | No | Prep time in minutes |

Example JSON Request:
```json
{
  "order_id": "<order_id>",
  "status": "PREPARING",
  "prep_time_min": 20
}
```

Example JSON Response:
```json
{
  "order": {
    "_id": "<order_id>",
    "status": "PREPARING"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 404 | {"detail": "Order not found"} |
| 403 | {"detail": "Role not allowed"} |

### Restaurant Ops: Toggle Menu Item
Endpoint: `POST /api/v1/restaurant/item/toggle`
Purpose: Toggle menu item availability.
Authentication: JWT
Roles: RESTAURANT
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| menu_item_id | string | Yes | Menu item id |
| is_available | boolean | Yes | Availability flag |

Example JSON Request:
```json
{
  "menu_item_id": "<menu_item_id>",
  "is_available": false
}
```

Example JSON Response:
```json
{
  "menu_item": {
    "_id": "<menu_item_id>",
    "is_available": false
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 404 | {"detail": "Menu item not found"} |
| 403 | {"detail": "Role not allowed"} |

### Restaurant Ops: Analytics
Endpoint: `GET /api/v1/restaurant/analytics`
Purpose: Retrieve analytics for a restaurant.
Authentication: JWT
Roles: RESTAURANT
Required Headers: `Authorization: Bearer <jwt>`

Path Params: None.

Query Params:
| Name | Type | Description |
| --- | --- | --- |
| restaurant_id | string | Required. Restaurant identifier. |

Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "analytics": {
    "orders": 120,
    "revenue": 450000
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "restaurant_id is required"} |
| 404 | {"detail": "Restaurant not found"} |
| 403 | {"detail": "Role not allowed"} |

## Admin APIs

### Admin: Overview
Endpoint: `GET /api/v1/admin/overview/`
Purpose: Fetch high-level admin metrics and overview data.
Authentication: JWT
Roles: ADMIN
Required Headers: `Authorization: Bearer <jwt>`

Path Params: None.
Query Params: None.
Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "overview": {
    "users": 1200,
    "orders": 3400
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 403 | {"detail": "Role not allowed"} |

### Admin: List Users
Endpoint: `GET /api/v1/admin/users/`
Purpose: List users for admin review.
Authentication: JWT
Roles: ADMIN
Required Headers: `Authorization: Bearer <jwt>`

Path Params: None.

Query Params:
| Name | Type | Description |
| --- | --- | --- |
| limit | integer | Optional. Default 50. |
| skip | integer | Optional. Default 0. |

Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "users": [
    {"_id": "<user_id>", "phone": "+919999999999", "role": "USER"}
  ]
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 403 | {"detail": "Role not allowed"} |

### Admin: List Captains
Endpoint: `GET /api/v1/admin/captains/`
Purpose: List captains for admin review.
Authentication: JWT
Roles: ADMIN
Required Headers: `Authorization: Bearer <jwt>`

Path Params: None.

Query Params:
| Name | Type | Description |
| --- | --- | --- |
| limit | integer | Optional. Default 50. |
| skip | integer | Optional. Default 0. |

Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "captains": [
    {"_id": "<captain_id>", "user_id": "<user_id>", "is_verified": false}
  ]
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 403 | {"detail": "Role not allowed"} |

### Admin: Go-Home Captains
Endpoint: `GET /api/v1/admin/go-home-captains/`
Purpose: List captains currently in go-home mode.
Authentication: JWT
Roles: ADMIN
Required Headers: `Authorization: Bearer <jwt>`

Path Params: None.

Query Params:
| Name | Type | Description |
| --- | --- | --- |
| limit | integer | Optional. Default 100. |

Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "captains": [
    {"_id": "<captain_id>", "go_home": true}
  ]
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 403 | {"detail": "Role not allowed"} |

### Admin: Verify Captain
Endpoint: `POST /api/v1/admin/captain/<captain_id>/verify/`
Purpose: Verify or unverify a captain.
Authentication: JWT
Roles: ADMIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params:
| Name | Type | Description |
| --- | --- | --- |
| captain_id | string | Captain identifier |

Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| is_verified | boolean | Yes | Verification status |
| reason | string | No | Optional reason |

Example JSON Request:
```json
{
  "is_verified": true,
  "reason": "Documents verified"
}
```

Example JSON Response:
```json
{
  "captain": {
    "_id": "<captain_id>",
    "is_verified": true
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 404 | {"detail": "Captain not found"} |
| 403 | {"detail": "Role not allowed"} |

### Admin: Recommend Restaurant
Endpoint: `POST /api/v1/admin/recommend/restaurant`
Purpose: Mark or unmark a restaurant as recommended.
Authentication: JWT
Roles: ADMIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| restaurant_id | string | Yes | Restaurant id |
| is_recommended | boolean | No | Default true |

Example JSON Request:
```json
{
  "restaurant_id": "<restaurant_id>",
  "is_recommended": true
}
```

Example JSON Response:
```json
{
  "restaurant": {
    "_id": "<restaurant_id>",
    "is_recommended": true
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 404 | {"detail": "Restaurant not found"} |
| 403 | {"detail": "Role not allowed"} |

### Admin: Recommend Menu Item
Endpoint: `POST /api/v1/admin/recommend/menu`
Purpose: Mark or unmark a menu item as recommended.
Authentication: JWT
Roles: ADMIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| menu_item_id | string | Yes | Menu item id |
| is_recommended | boolean | No | Default true |

Example JSON Request:
```json
{
  "menu_item_id": "<menu_item_id>",
  "is_recommended": true
}
```

Example JSON Response:
```json
{
  "menu_item": {
    "_id": "<menu_item_id>",
    "is_recommended": true
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 404 | {"detail": "Menu item not found"} |
| 403 | {"detail": "Role not allowed"} |

### Admin: Recommendations List
Endpoint: `GET /api/v1/admin/recommendations/`
Purpose: List legacy recommendations.
Authentication: JWT
Roles: ADMIN
Required Headers: `Authorization: Bearer <jwt>`

Path Params: None.
Query Params: None.
Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "recommendations": [
    {"_id": "<recommendation_id>", "type": "RESTAURANT", "title": "Top Rated"}
  ]
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 403 | {"detail": "Role not allowed"} |

### Admin: Create Recommendation
Endpoint: `POST /api/v1/admin/recommendations/`
Purpose: Create a legacy recommendation entry.
Authentication: JWT
Roles: ADMIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| type | string | Yes | RESTAURANT or MENU_ITEM |
| reference_id | string | Yes | Target entity id |
| title | string | Yes | Recommendation title |
| description | string | Yes | Description |

Example JSON Request:
```json
{
  "type": "RESTAURANT",
  "reference_id": "<restaurant_id>",
  "title": "Top Rated",
  "description": "Chef specials"
}
```

Example JSON Response:
```json
{
  "recommendation": {
    "_id": "<recommendation_id>",
    "type": "RESTAURANT",
    "reference_id": "<restaurant_id>"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Invalid reference id"} |
| 403 | {"detail": "Role not allowed"} |

### Admin: Delete Recommendation
Endpoint: `DELETE /api/v1/admin/recommendations/<recommendation_id>/`
Purpose: Delete a legacy recommendation entry.
Authentication: JWT
Roles: ADMIN
Required Headers: `Authorization: Bearer <jwt>`

Path Params:
| Name | Type | Description |
| --- | --- | --- |
| recommendation_id | string | Recommendation id |

Query Params: None.
Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "deleted": true
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 404 | {"detail": "Recommendation not found"} |
| 403 | {"detail": "Role not allowed"} |

### Vehicles: Update Rules
Endpoint: `POST /api/v1/vehicle/rules`
Purpose: Update vehicle rules (admin-only).
Authentication: JWT
Roles: ADMIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| food_allowed_vehicles | array<string> | No | Allowed vehicle types |
| ev_reward_percentage | number | No | EV reward percentage |
| ev_bonus_multiplier | number | No | EV bonus multiplier |

Example JSON Request:
```json
{
  "food_allowed_vehicles": ["BIKE_PETROL", "BIKE_EV"],
  "ev_reward_percentage": 0.1,
  "ev_bonus_multiplier": 1.2
}
```

Example JSON Response:
```json
{
  "rules": {
    "food_allowed_vehicles": ["BIKE_PETROL", "BIKE_EV"],
    "ev_reward_percentage": 0.1,
    "ev_bonus_multiplier": 1.2
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 403 | {"detail": "Not allowed"} |

## Notification APIs

### Notifications: Send
Endpoint: `POST /api/v1/notify/send`
Purpose: Queue an immediate push notification.
Authentication: JWT
Roles: ADMIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| user_id | string | No | Target user id |
| topic | string | No | FCM topic name |
| title | string | Yes | Notification title |
| body | string | No | Notification body |
| data | object | No | Custom payload |
| priority | string | No | LOW, NORMAL, HIGH |
| silent | boolean | No | Default false |

Example JSON Request:
```json
{
  "user_id": "<user_id>",
  "title": "Order placed",
  "body": "Your order is being prepared",
  "data": {"order_id": "<order_id>"},
  "priority": "HIGH"
}
```

Example JSON Response:
```json
{
  "notification": {
    "_id": "<notification_id>",
    "status": "QUEUED",
    "retry_count": 0
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"title": ["This field is required."]} |
| 403 | {"detail": "Role not allowed"} |

### Notifications: Schedule
Endpoint: `POST /api/v1/notify/schedule`
Purpose: Schedule a notification for future delivery.
Authentication: JWT
Roles: ADMIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| user_id | string | No | Target user id |
| topic | string | No | FCM topic name |
| title | string | Yes | Notification title |
| body | string | No | Notification body |
| data | object | No | Custom payload |
| priority | string | No | LOW, NORMAL, HIGH |
| silent | boolean | No | Default false |
| send_at | string | Yes | ISO 8601 datetime |

Example JSON Request:
```json
{
  "user_id": "<user_id>",
  "title": "Promo",
  "body": "Discount available",
  "send_at": "2026-02-11T12:00:00Z"
}
```

Example JSON Response:
```json
{
  "notification": {
    "_id": "<notification_id>",
    "status": "SCHEDULED",
    "send_at": "2026-02-11T12:00:00Z"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"send_at": ["This field is required."]} |
| 403 | {"detail": "Role not allowed"} |

### Notifications: History
Endpoint: `GET /api/v1/notify/history`
Purpose: List notification history.
Authentication: JWT
Roles: ADMIN
Required Headers: `Authorization: Bearer <jwt>`

Path Params: None.

Query Params:
| Name | Type | Description |
| --- | --- | --- |
| limit | integer | Optional. Default 50. |

Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "notifications": [
    {"_id": "<notification_id>", "status": "SENT", "title": "Order placed"}
  ]
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 403 | {"detail": "Role not allowed"} |

### Notifications: Retry
Endpoint: `POST /api/v1/notify/retry/<notification_id>`
Purpose: Retry a failed or queued notification.
Authentication: JWT
Roles: ADMIN
Required Headers: `Authorization: Bearer <jwt>`

Path Params:
| Name | Type | Description |
| --- | --- | --- |
| notification_id | string | Notification id |

Query Params: None.
Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "queued": true
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 404 | {"detail": "Notification not found"} |
| 403 | {"detail": "Role not allowed"} |

## Trust/Fraud APIs

### Trust: Register Device
Endpoint: `POST /api/v1/trust/device/register`
Purpose: Register a device for trust/risk analysis.
Authentication: JWT
Roles: USER, CAPTAIN, RESTAURANT, ADMIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| device_id | string | Yes | Device identifier |
| platform | string | No | Platform name |
| fingerprint | string | No | Device fingerprint |
| ip | string | No | IP address |
| meta | object | No | Metadata (e.g., location flags) |

Example JSON Request:
```json
{
  "device_id": "device-123",
  "platform": "android",
  "fingerprint": "hash",
  "meta": {"mock_location": false}
}
```

Example JSON Response:
```json
{
  "device": {
    "device_id": "device-123",
    "platform": "android"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"device_id": ["This field is required."]} |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Trust: Scan
Endpoint: `GET /api/v1/trust/scan`
Purpose: Run a trust scan for duplicate devices and related signals.
Authentication: JWT
Roles: ADMIN
Required Headers: `Authorization: Bearer <jwt>`

Path Params: None.

Query Params:
| Name | Type | Description |
| --- | --- | --- |
| user_id | string | Optional. Filter by user id. |

Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "findings": [
    {"device_id": "device-123", "type": "DUPLICATE_DEVICE", "users": ["<user_id>"]}
  ],
  "device_count": 10
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 403 | {"detail": "Role not allowed"} |

### Trust: Risk Score
Endpoint: `POST /api/v1/trust/risk-score`
Purpose: Calculate a risk score for a user and device.
Authentication: JWT
Roles: USER, CAPTAIN, RESTAURANT, ADMIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| user_id | string | Yes | User id |
| device_id | string | No | Device id |

Example JSON Request:
```json
{
  "user_id": "<user_id>",
  "device_id": "device-123"
}
```

Example JSON Response:
```json
{
  "user_id": "<user_id>",
  "risk_score": 45,
  "reasons": [
    {"type": "DEVICE_REUSE", "detail": "device used by multiple users"}
  ]
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Fraud: Scan Users
Endpoint: `GET /api/v1/fraud/scan/`
Purpose: Run a fraud scan and return suspicious users.
Authentication: JWT
Roles: ADMIN
Required Headers: `Authorization: Bearer <jwt>`

Path Params: None.

Query Params:
| Name | Type | Description |
| --- | --- | --- |
| limit | integer | Optional. Default 200. |

Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "suspicious": [
    {
      "user_id": "<user_id>",
      "score": -0.42,
      "features": {"wallet_credit": 200000, "ride_count": 2}
    }
  ]
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 403 | {"detail": "Role not allowed"} |

## Chat APIs

### Chat: History
Endpoint: `GET /api/v1/chat/history/<room_id>`
Purpose: Fetch recent messages from a chat room.
Authentication: JWT
Roles: USER, CAPTAIN, RESTAURANT, ADMIN
Required Headers: `Authorization: Bearer <jwt>`

Path Params:
| Name | Type | Description |
| --- | --- | --- |
| room_id | string | Chat room id |

Query Params:
| Name | Type | Description |
| --- | --- | --- |
| limit | integer | Optional. 1 to 200. Default 50. |

Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "messages": [
    {
      "_id": "<message_id>",
      "room_id": "<room_id>",
      "text": "Hello"
    }
  ]
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 403 | {"detail": "Not allowed"} |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Chat: Masked Call
Endpoint: `GET /api/v1/chat/call/<room_id>`
Purpose: Get masked phone numbers for a call between participants.
Authentication: JWT
Roles: USER, CAPTAIN, RESTAURANT
Required Headers: `Authorization: Bearer <jwt>`

Path Params:
| Name | Type | Description |
| --- | --- | --- |
| room_id | string | Chat room id |

Query Params:
| Name | Type | Description |
| --- | --- | --- |
| callee_id | string | Required. Target user id. |

Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "call": {
    "caller": "+1-555-***-1234",
    "callee": "+1-555-***-5678"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "callee_id is required"} |
| 403 | {"detail": "Not allowed"} |

### Chat: Read Receipt
Endpoint: `POST /api/v1/chat/read`
Purpose: Mark a room or message as read.
Authentication: JWT
Roles: USER, CAPTAIN, RESTAURANT, ADMIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| room_id | string | Yes | Chat room id |
| message_id | string | No | Message id |

Example JSON Request:
```json
{
  "room_id": "<room_id>",
  "message_id": "<message_id>"
}
```

Example JSON Response:
```json
{
  "read": {
    "room_id": "<room_id>",
    "last_read_message_id": "<message_id>"
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 403 | {"detail": "Not allowed"} |

### Chat: Typing Indicator
Endpoint: `POST /api/v1/chat/typing`
Purpose: Record typing events for a room.
Authentication: JWT
Roles: USER, CAPTAIN, RESTAURANT, ADMIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| room_id | string | Yes | Chat room id |
| is_typing | boolean | Yes | Typing state |

Example JSON Request:
```json
{
  "room_id": "<room_id>",
  "is_typing": true
}
```

Example JSON Response:
```json
{
  "typing": {
    "room_id": "<room_id>",
    "is_typing": true
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 403 | {"detail": "Not allowed"} |

## Wallet/Ledger APIs

### Wallet: Transactions
Endpoint: `GET /api/v1/wallet/transactions/`
Purpose: List wallet transactions for the authenticated user.
Authentication: JWT
Roles: Any authenticated
Required Headers: `Authorization: Bearer <jwt>`

Path Params: None.
Query Params: None.
Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "transactions": [
    {"_id": "<txn_id>", "type": "DEBIT", "amount": 2500, "reason": "FOOD_ORDER"}
  ]
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Wallet: Refund
Endpoint: `POST /api/v1/wallet/refund/`
Purpose: Create a wallet refund transaction.
Authentication: JWT
Roles: USER
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| reference | string | No | Reference id (order/ride) |
| amount | integer | Yes | Refund amount |
| reason | string | Yes | Refund reason |
| source | string | Yes | FOOD, RIDE, REFUND |

Example JSON Request:
```json
{
  "reference": "<order_id>",
  "amount": 5000,
  "reason": "Order cancelled",
  "source": "FOOD"
}
```

Example JSON Response:
```json
{
  "transaction": {
    "_id": "<txn_id>",
    "type": "CREDIT",
    "amount": 5000
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Refund failed"} |
| 403 | {"detail": "Role not allowed"} |

### Wallet: Ledger
Endpoint: `GET /api/v1/wallet/ledger`
Purpose: List ledger entries for the authenticated user.
Authentication: JWT
Roles: Any authenticated
Required Headers: `Authorization: Bearer <jwt>`

Path Params: None.

Query Params:
| Name | Type | Description |
| --- | --- | --- |
| limit | integer | Optional. Default 50. |

Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "entries": [
    {"_id": "<entry_id>", "direction": "DEBIT", "amount": 2500}
  ]
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Wallet: Settle
Endpoint: `POST /api/v1/wallet/settle`
Purpose: Run settlement for completed orders and rides.
Authentication: JWT
Roles: ADMIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| limit | integer | No | 1 to 500 (default 50) |

Example JSON Request:
```json
{
  "limit": 50
}
```

Example JSON Response:
```json
{
  "settled": [
    {"reference_type": "ORDER", "amount": 45000}
  ]
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 403 | {"detail": "Role not allowed"} |

### Wallet: Analytics
Endpoint: `GET /api/v1/wallet/analytics/<user_id>/`
Purpose: Fetch wallet analytics for a user (admins) or self (users).
Authentication: JWT
Roles: USER, ADMIN
Required Headers: `Authorization: Bearer <jwt>`

Path Params:
| Name | Type | Description |
| --- | --- | --- |
| user_id | string | Target user id |

Query Params: None.
Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "analytics": {
    "totals": {"credits": 200000, "debits": 150000, "rewards": 5000, "refunds": 1000},
    "daily": {"2026-02-10": {"credits": 2000, "debits": 1500, "rewards": 0, "refunds": 0}}
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 403 | {"detail": "Not allowed"} |
| 404 | {"detail": "User not found"} |

## Matching/Jobs

### Jobs: Create
Endpoint: `POST /api/v1/jobs/create/`
Purpose: Create a matching job for an order or ride.
Authentication: JWT
Roles: USER, RESTAURANT
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| job_type | string | Yes | ORDER or RIDE |
| job_id | string | Yes | Order or ride id |

Example JSON Request:
```json
{
  "job_type": "ORDER",
  "job_id": "<order_id>"
}
```

Example JSON Response:
```json
{
  "candidates": ["<captain_id>"]
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Invalid job_type"} |
| 403 | {"detail": "Role not allowed"} |

### Jobs: Accept
Endpoint: `POST /api/v1/jobs/accept/`
Purpose: Accept a matching job (captain action).
Authentication: JWT
Roles: CAPTAIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| job_type | string | Yes | ORDER or RIDE |
| job_id | string | Yes | Order or ride id |

Example JSON Request:
```json
{
  "job_type": "ORDER",
  "job_id": "<order_id>"
}
```

Example JSON Response:
```json
{
  "job": {
    "user_id": "<captain_id>",
    "current_job_id": "<order_id>",
    "current_job_type": "ORDER",
    "is_busy": true
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Job not found"} |
| 403 | {"detail": "Role not allowed"} |

### Jobs: Reject
Endpoint: `POST /api/v1/jobs/reject/`
Purpose: Reject a matching job (captain action).
Authentication: JWT
Roles: CAPTAIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| job_type | string | Yes | ORDER or RIDE |
| job_id | string | Yes | Order or ride id |

Example JSON Request:
```json
{
  "job_type": "RIDE",
  "job_id": "<ride_id>"
}
```

Example JSON Response:
```json
{
  "rejected": true
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Job not found"} |
| 403 | {"detail": "Role not allowed"} |

### Jobs: Complete
Endpoint: `POST /api/v1/jobs/complete/`
Purpose: Complete a matching job (captain action).
Authentication: JWT
Roles: CAPTAIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| job_type | string | Yes | ORDER or RIDE |
| job_id | string | Yes | Order or ride id |

Example JSON Request:
```json
{
  "job_type": "RIDE",
  "job_id": "<ride_id>"
}
```

Example JSON Response:
```json
{
  "job": {
    "user_id": "<captain_id>",
    "current_job_id": null,
    "current_job_type": null,
    "is_busy": false
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Job not found"} |
| 403 | {"detail": "Role not allowed"} |

### Jobs: Accept (Legacy Captain Path)
Endpoint: `POST /api/v1/captains/accept-job/`
Purpose: Accept a matching job (legacy captain path).
Authentication: JWT
Roles: CAPTAIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| job_type | string | Yes | ORDER or RIDE |
| job_id | string | Yes | Order or ride id |

Example JSON Request:
```json
{
  "job_type": "ORDER",
  "job_id": "<order_id>"
}
```

Example JSON Response:
```json
{
  "job": {
    "user_id": "<captain_id>",
    "current_job_id": "<order_id>",
    "current_job_type": "ORDER",
    "is_busy": true
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Job not found"} |
| 403 | {"detail": "Role not allowed"} |

### Jobs: Complete (Legacy Captain Path)
Endpoint: `POST /api/v1/captains/complete-job/`
Purpose: Complete a matching job (legacy captain path).
Authentication: JWT
Roles: CAPTAIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| job_type | string | Yes | ORDER or RIDE |
| job_id | string | Yes | Order or ride id |

Example JSON Request:
```json
{
  "job_type": "ORDER",
  "job_id": "<order_id>"
}
```

Example JSON Response:
```json
{
  "job": {
    "user_id": "<captain_id>",
    "current_job_id": null,
    "current_job_type": null,
    "is_busy": false
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Job not found"} |
| 403 | {"detail": "Role not allowed"} |

### Cancellation: Cancel Order
Endpoint: `POST /api/v1/cancel/order`
Purpose: Cancel an order with a reason and optional flags.
Authentication: JWT
Roles: USER, CAPTAIN, RESTAURANT, ADMIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| order_id | string | Yes | Order id |
| actor | string | No | USER, CAPTAIN, RESTAURANT, SYSTEM, ADMIN |
| reason | string | Yes | Cancellation reason |
| late_delivery | boolean | No | Late delivery flag |
| no_show | boolean | No | No-show flag |
| metadata | object | No | Additional data |

Example JSON Request:
```json
{
  "order_id": "<order_id>",
  "reason": "User cancelled",
  "late_delivery": false
}
```

Example JSON Response:
```json
{
  "result": {
    "cancellation": {
      "job_type": "ORDER",
      "job_id": "<order_id>",
      "actor_role": "USER",
      "reason": "User cancelled"
    },
    "refund": {
      "amount": 5000,
      "source": "CANCEL"
    },
    "penalty": null
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Invalid order id"} |
| 400 | {"detail": "Order not found"} |
| 400 | {"detail": "Order already closed"} |
| 401 | {"detail": "Authentication credentials were not provided"} |

### Cancellation: Cancel Ride
Endpoint: `POST /api/v1/cancel/ride`
Purpose: Cancel a ride with a reason and optional flags.
Authentication: JWT
Roles: USER, CAPTAIN, ADMIN
Required Headers: `Authorization: Bearer <jwt>`, `Content-Type: application/json`

Path Params: None.
Query Params: None.

Request Body Schema:
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| ride_id | string | Yes | Ride id |
| actor | string | No | USER, CAPTAIN, RESTAURANT, SYSTEM, ADMIN |
| reason | string | Yes | Cancellation reason |
| no_show | boolean | No | No-show flag |
| metadata | object | No | Additional data |

Example JSON Request:
```json
{
  "ride_id": "<ride_id>",
  "reason": "User cancelled"
}
```

Example JSON Response:
```json
{
  "result": {
    "cancellation": {
      "job_type": "RIDE",
      "job_id": "<ride_id>",
      "actor_role": "USER",
      "reason": "User cancelled"
    },
    "refund": {
      "amount": 3000,
      "source": "CANCEL"
    },
    "penalty": null
  }
}
```

Possible Errors:
| Status | Example |
| --- | --- |
| 400 | {"detail": "Invalid ride id"} |
| 400 | {"detail": "Ride not found"} |
| 400 | {"detail": "Ride already closed"} |
| 401 | {"detail": "Authentication credentials were not provided"} |

## Observability

### Health
Endpoint: `GET /api/v1/health`
Purpose: Health check endpoint (database ping).
Authentication: None
Roles: None
Required Headers: None

Path Params: None.
Query Params: None.
Request Body Schema: None.

Example JSON Request:
```json
{}
```

Example JSON Response:
```json
{
  "status": "ok",
  "timestamp": "2026-02-11T00:00:00Z"
}
```

Possible Errors: None (returns `status: degraded` on failure).

### Metrics
Endpoint: `GET /api/v1/metrics`
Purpose: Prometheus metrics endpoint.
Authentication: None
Roles: None
Required Headers: None

Path Params: None.
Query Params: None.
Request Body Schema: None.

Example Request:
```text
GET /api/v1/metrics
```

Example Response:
```text
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",path="/api/v1/health",status="200"} 42
```

Possible Errors:
| Status | Example |
| --- | --- |
| 501 | prometheus_client not installed |

## WebSocket APIs

### WS: Captain Channel
URI: `ws://<host>/ws/captain/<captain_id>/`
Purpose: Real-time job offers and status updates for captains.
Authentication: None enforced at consumer (connection uses `AuthMiddlewareStack`).
Required Headers: None

Path Params:
| Name | Type | Description |
| --- | --- | --- |
| captain_id | string | Captain user id |

Query Params: None.

Example Messages (client -> server):
```json
{"type": "ping"}
```

Example Messages (server -> client):
```json
{"type": "pong"}
```
```json
{"type": "job_offer", "data": {"job_id": "<order_or_ride_id>"}}
```
```json
{"type": "job_assigned", "data": {"job_id": "<order_or_ride_id>"}}
```
```json
{"type": "job_status", "data": {"status": "ASSIGNED"}}
```

### WS: User Channel
URI: `ws://<host>/ws/user/<user_id>/`
Purpose: Real-time updates for users (assignments, status, location updates).
Authentication: None enforced at consumer (connection uses `AuthMiddlewareStack`).
Required Headers: None

Path Params:
| Name | Type | Description |
| --- | --- | --- |
| user_id | string | User id |

Query Params: None.

Example Messages (client -> server):
```json
{"type": "ping"}
```

Example Messages (server -> client):
```json
{"type": "pong"}
```
```json
{"type": "job_assigned", "data": {"job_id": "<order_or_ride_id>"}}
```
```json
{"type": "location_update", "data": {"lat": 12.97, "lng": 77.59}}
```
```json
{"type": "job_status", "data": {"status": "EN_ROUTE"}}
```

### WS: Order Tracking
URI: `ws://<host>/ws/order/<order_id>/`
Purpose: Order tracking updates (typically captain location updates).
Authentication: None enforced at consumer (connection uses `AuthMiddlewareStack`).
Required Headers: None

Path Params:
| Name | Type | Description |
| --- | --- | --- |
| order_id | string | Order id |

Query Params: None.

Example Messages (client -> server):
```json
{"type": "ping"}
```

Example Messages (server -> client):
```json
{"type": "pong"}
```
```json
{"type": "location_update", "data": {"lat": 12.97, "lng": 77.59}}
```

### WS: Chat Room
URI: `ws://<host>/ws/chat/<room_id>/`
Purpose: Real-time chat between users, captains, and restaurants.
Authentication: None enforced at consumer (connection uses `AuthMiddlewareStack`).
Required Headers: None

Path Params:
| Name | Type | Description |
| --- | --- | --- |
| room_id | string | Chat room id |

Query Params: None.

Example Messages (client -> server):
```json
{
  "type": "message",
  "sender_id": "<user_id>",
  "sender_role": "USER",
  "receiver_id": "<captain_id>",
  "receiver_role": "CAPTAIN",
  "message": "On my way",
  "client_message_id": "msg_123"
}
```
```json
{"type": "delivered", "message_id": "<message_id>", "user_id": "<user_id>"}
```
```json
{"type": "ping"}
```

Example Messages (server -> client):
```json
{"type": "ack", "message_id": "<message_id>"}
```
```json
{"type": "message", "data": {"message": {"id": "<message_id>", "room_id": "<room_id>", "text": "On my way"}}}
```
```json
{"type": "error", "detail": "Invalid message"}
```
