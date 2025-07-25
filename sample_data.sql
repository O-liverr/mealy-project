INSERT INTO Users (user_id, username, email, password_hash, role)
VALUES (1, 'john_doe', 'john@example.com', '$2b$12$QijG27gCkkVic2aBPQroZeX7heK6PSttS3.NTCaxvdlYokJ6EXdtS', 'customer'),
       (2, 'caterer1', 'caterer1@example.com', '$2b$12$kbYS.v5OcJlf0cDqBKGPju/p9fKKQWPkEyVYE7REfNQcd61lrx/Ja', 'admin')
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO Caterers (caterer_id, user_id, name, description)
VALUES (1, 2, 'Tasty Bites', 'Healthy meals daily')
ON CONFLICT (caterer_id) DO NOTHING;

INSERT INTO MealOptions (meal_option_id, caterer_id, name, description, price, category, created_at)
VALUES (1, 1, 'Beef with Rice', 'Grilled beef with steamed rice', 10.50, 'Main', CURRENT_TIMESTAMP),
       (2, 1, 'Chicken with Fries', 'Fried chicken with crispy fries', 8.75, 'Main', CURRENT_TIMESTAMP)
ON CONFLICT (meal_option_id) DO NOTHING;

INSERT INTO Menus (menu_id, caterer_id, menu_date, created_at)
VALUES (1, 1, '2025-07-25', CURRENT_TIMESTAMP)
ON CONFLICT (menu_id) DO NOTHING;

INSERT INTO MenuMealOptions (menu_id, meal_option_id)
VALUES (1, 1), (1, 2)
ON CONFLICT (menu_id, meal_option_id) DO NOTHING;

INSERT INTO Orders (order_id, user_id, menu_id, meal_option_id, status, created_at)
VALUES (1, 1, 1, 1, 'pending', CURRENT_TIMESTAMP)
ON CONFLICT (order_id) DO NOTHING;

INSERT INTO Notifications (notification_id, user_id, menu_id, message, created_at)
VALUES (1, 1, 1, 'Menu for 2025-07-25 is set!', CURRENT_TIMESTAMP)
ON CONFLICT (notification_id) DO NOTHING;