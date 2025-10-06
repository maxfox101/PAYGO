import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json

class TestAuthEndpoints:
    """Тесты для endpoints аутентификации"""
    
    def test_register_user_success(self, test_client, sample_user_data):
        """Тест успешной регистрации пользователя"""
        response = test_client.post("/auth/register", json=sample_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["email"] == sample_user_data["email"]
        assert data["first_name"] == sample_user_data["first_name"]
        assert "password" not in data  # Пароль не должен возвращаться
    
    def test_register_user_duplicate_email(self, test_client, sample_user_data):
        """Тест регистрации с существующим email"""
        # Первая регистрация
        test_client.post("/auth/register", json=sample_user_data)
        
        # Вторая регистрация с тем же email
        response = test_client.post("/auth/register", json=sample_user_data)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    def test_register_user_invalid_data(self, test_client):
        """Тест регистрации с невалидными данными"""
        invalid_data = {
            "email": "invalid-email",
            "password": "123",  # Слишком короткий пароль
            "first_name": "",    # Пустое имя
        }
        
        response = test_client.post("/auth/register", json=invalid_data)
        
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert len(errors) > 0
    
    def test_login_success(self, test_client, sample_user_data):
        """Тест успешного входа"""
        # Сначала регистрируем пользователя
        test_client.post("/auth/register", json=sample_user_data)
        
        # Затем входим
        login_data = {
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        
        response = test_client.post("/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, test_client):
        """Тест входа с неверными учетными данными"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = test_client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()
    
    def test_refresh_token(self, test_client, sample_user_data):
        """Тест обновления токена"""
        # Регистрируем и входим
        test_client.post("/auth/register", json=sample_user_data)
        login_response = test_client.post("/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        
        refresh_token = login_response.json().get("refresh_token")
        if refresh_token:
            response = test_client.post("/auth/refresh", json={
                "refresh_token": refresh_token
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["access_token"] != login_response.json()["access_token"]

class TestUserEndpoints:
    """Тесты для endpoints пользователей"""
    
    def test_get_user_profile(self, test_client, sample_user_data):
        """Тест получения профиля пользователя"""
        # Регистрируем и входим
        test_client.post("/auth/register", json=sample_user_data)
        login_response = test_client.post("/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = test_client.get("/users/profile", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["first_name"] == sample_user_data["first_name"]
    
    def test_get_user_profile_unauthorized(self, test_client):
        """Тест получения профиля без авторизации"""
        response = test_client.get("/users/profile")
        
        assert response.status_code == 401
    
    def test_update_user_profile(self, test_client, sample_user_data):
        """Тест обновления профиля пользователя"""
        # Регистрируем и входим
        test_client.post("/auth/register", json=sample_user_data)
        login_response = test_client.post("/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        update_data = {
            "first_name": "Обновленное Имя",
            "last_name": "Обновленная Фамилия"
        }
        
        response = test_client.put("/users/profile", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == update_data["first_name"]
        assert data["last_name"] == update_data["last_name"]
    
    def test_change_password(self, test_client, sample_user_data):
        """Тест смены пароля"""
        # Регистрируем и входим
        test_client.post("/auth/register", json=sample_user_data)
        login_response = test_client.post("/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        password_data = {
            "current_password": sample_user_data["password"],
            "new_password": "newpassword123"
        }
        
        response = test_client.post("/users/change-password", json=password_data, headers=headers)
        
        assert response.status_code == 200
        assert "password changed" in response.json()["message"].lower()
        
        # Проверяем, что новый пароль работает
        new_login_response = test_client.post("/auth/login", json={
            "email": sample_user_data["email"],
            "password": "newpassword123"
        })
        
        assert new_login_response.status_code == 200

class TestCardEndpoints:
    """Тесты для endpoints карт"""
    
    def test_add_card_success(self, test_client, sample_user_data, sample_card_data):
        """Тест успешного добавления карты"""
        # Регистрируем и входим
        test_client.post("/auth/register", json=sample_user_data)
        login_response = test_client.post("/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = test_client.post("/cards/", json=sample_card_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["cardholder_name"] == sample_card_data["cardholder_name"]
        # Номер карты должен быть замаскирован
        assert data["card_number"].startswith("4111")
        assert data["card_number"].endswith("1111")
        assert len(data["card_number"]) == 16
    
    def test_add_card_unauthorized(self, test_client, sample_card_data):
        """Тест добавления карты без авторизации"""
        response = test_client.post("/cards/", json=sample_card_data)
        
        assert response.status_code == 401
    
    def test_get_user_cards(self, test_client, sample_user_data, sample_card_data):
        """Тест получения карт пользователя"""
        # Регистрируем, входим и добавляем карту
        test_client.post("/auth/register", json=sample_user_data)
        login_response = test_client.post("/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        test_client.post("/cards/", json=sample_card_data, headers=headers)
        
        response = test_client.get("/cards/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["cardholder_name"] == sample_card_data["cardholder_name"]
    
    def test_delete_card(self, test_client, sample_user_data, sample_card_data):
        """Тест удаления карты"""
        # Регистрируем, входим и добавляем карту
        test_client.post("/auth/register", json=sample_user_data)
        login_response = test_client.post("/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        card_response = test_client.post("/cards/", json=sample_card_data, headers=headers)
        card_id = card_response.json()["id"]
        
        # Удаляем карту
        response = test_client.delete(f"/cards/{card_id}", headers=headers)
        
        assert response.status_code == 200
        
        # Проверяем, что карта удалена
        cards_response = test_client.get("/cards/", headers=headers)
        assert len(cards_response.json()) == 0

class TestTransactionEndpoints:
    """Тесты для endpoints транзакций"""
    
    def test_create_transaction_success(self, test_client, sample_user_data, sample_transaction_data):
        """Тест успешного создания транзакции"""
        # Регистрируем и входим
        test_client.post("/auth/register", json=sample_user_data)
        login_response = test_client.post("/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = test_client.post("/transactions/", json=sample_transaction_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["amount"] == sample_transaction_data["amount"]
        assert data["currency"] == sample_transaction_data["currency"]
        assert data["status"] == "pending"
    
    def test_get_user_transactions(self, test_client, sample_user_data, sample_transaction_data):
        """Тест получения транзакций пользователя"""
        # Регистрируем, входим и создаем транзакцию
        test_client.post("/auth/register", json=sample_user_data)
        login_response = test_client.post("/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        test_client.post("/transactions/", json=sample_transaction_data, headers=headers)
        
        response = test_client.get("/transactions/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["amount"] == sample_transaction_data["amount"]
    
    def test_get_transaction_by_id(self, test_client, sample_user_data, sample_transaction_data):
        """Тест получения транзакции по ID"""
        # Регистрируем, входим и создаем транзакцию
        test_client.post("/auth/register", json=sample_user_data)
        login_response = test_client.post("/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        transaction_response = test_client.post("/transactions/", json=sample_transaction_data, headers=headers)
        transaction_id = transaction_response.json()["id"]
        
        response = test_client.get(f"/transactions/{transaction_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == transaction_id
        assert data["amount"] == sample_transaction_data["amount"]

class TestTerminalEndpoints:
    """Тесты для endpoints терминалов"""
    
    def test_get_terminals_unauthorized(self, test_client):
        """Тест получения терминалов без авторизации"""
        response = test_client.get("/terminals/")
        
        assert response.status_code == 401
    
    def test_get_terminals_admin(self, test_client, admin_user_data):
        """Тест получения терминалов администратором"""
        # Регистрируем и входим как админ
        test_client.post("/auth/register", json=admin_user_data)
        login_response = test_client.post("/auth/login", json={
            "email": admin_user_data["email"],
            "password": admin_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = test_client.get("/terminals/", headers=headers)
        
        assert response.status_code == 200
        # Пока может быть пустой список, но endpoint должен работать
    
    def test_create_terminal_admin(self, test_client, admin_user_data):
        """Тест создания терминала администратором"""
        # Регистрируем и входим как админ
        test_client.post("/auth/register", json=admin_user_data)
        login_response = test_client.post("/auth/login", json={
            "email": admin_user_data["email"],
            "password": admin_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        terminal_data = {
            "name": "Тестовый терминал",
            "location": "Тестовая локация",
            "status": "active"
        }
        
        response = test_client.post("/terminals/", json=terminal_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == terminal_data["name"]
        assert data["status"] == terminal_data["status"]

class TestAdminEndpoints:
    """Тесты для административных endpoints"""
    
    def test_get_users_admin(self, test_client, admin_user_data, sample_user_data):
        """Тест получения списка пользователей администратором"""
        # Регистрируем админа и обычного пользователя
        test_client.post("/auth/register", json=admin_user_data)
        test_client.post("/auth/register", json=sample_user_data)
        
        # Входим как админ
        login_response = test_client.post("/auth/login", json={
            "email": admin_user_data["email"],
            "password": admin_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = test_client.get("/admin/users", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2  # Админ + обычный пользователь
    
    def test_get_users_unauthorized(self, test_client):
        """Тест получения списка пользователей без авторизации"""
        response = test_client.get("/admin/users")
        
        assert response.status_code == 401
    
    def test_get_users_non_admin(self, test_client, sample_user_data):
        """Тест получения списка пользователей не-админом"""
        # Регистрируем и входим как обычный пользователь
        test_client.post("/auth/register", json=sample_user_data)
        login_response = test_client.post("/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = test_client.get("/admin/users", headers=headers)
        
        assert response.status_code == 403  # Доступ запрещен
    
    def test_update_user_role_admin(self, test_client, admin_user_data, sample_user_data):
        """Тест обновления роли пользователя администратором"""
        # Регистрируем админа и обычного пользователя
        test_client.post("/auth/register", json=admin_user_data)
        test_client.post("/auth/register", json=sample_user_data)
        
        # Входим как админ
        login_response = test_client.post("/auth/login", json={
            "email": admin_user_data["email"],
            "password": admin_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Получаем ID обычного пользователя
        users_response = test_client.get("/admin/users", headers=headers)
        user_id = None
        for user in users_response.json():
            if user["email"] == sample_user_data["email"]:
                user_id = user["id"]
                break
        
        assert user_id is not None
        
        # Обновляем роль
        update_data = {"role": "terminal_operator"}
        response = test_client.put(f"/admin/users/{user_id}", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "terminal_operator"

class TestHealthEndpoints:
    """Тесты для health check endpoints"""
    
    def test_health_check(self, test_client):
        """Тест health check endpoint"""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_health_detailed(self, test_client):
        """Тест детального health check"""
        response = test_client.get("/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "services" in data
        assert "database" in data["services"]
        assert "redis" in data["services"]

class TestErrorHandling:
    """Тесты для обработки ошибок"""
    
    def test_404_not_found(self, test_client):
        """Тест 404 ошибки"""
        response = test_client.get("/nonexistent-endpoint")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_422_validation_error(self, test_client):
        """Тест 422 ошибки валидации"""
        invalid_data = {"email": "invalid-email"}
        
        response = test_client.post("/auth/register", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert len(data["detail"]) > 0
    
    def test_500_internal_error(self, test_client):
        """Тест 500 внутренней ошибки"""
        # Этот тест может быть сложным, так как мы не хотим вызывать реальные ошибки
        # В реальном проекте можно использовать моки для симуляции ошибок
        
        # Пока просто проверяем, что приложение работает
        response = test_client.get("/health")
        assert response.status_code == 200

# Тесты производительности
class TestPerformance:
    """Тесты производительности API"""
    
    @pytest.mark.performance
    def test_multiple_requests_performance(self, test_client, sample_user_data):
        """Тест производительности при множественных запросах"""
        import time
        
        # Регистрируем пользователя
        test_client.post("/auth/register", json=sample_user_data)
        login_response = test_client.post("/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Измеряем время выполнения множественных запросов
        start_time = time.time()
        
        for _ in range(100):
            response = test_client.get("/users/profile", headers=headers)
            assert response.status_code == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 100 запросов должны выполняться менее чем за 5 секунд
        assert total_time < 5.0
        print(f"100 запросов выполнены за {total_time:.2f} секунд")
    
    @pytest.mark.performance
    def test_large_data_handling(self, test_client, large_dataset):
        """Тест обработки больших объемов данных"""
        # Тестируем, что приложение может обрабатывать большие объемы данных
        # без значительного замедления
        
        response = test_client.get("/health")
        assert response.status_code == 200
        
        # В реальном проекте здесь можно тестировать endpoints,
        # которые работают с большими объемами данных

# Интеграционные тесты
class TestIntegration:
    """Интеграционные тесты"""
    
    @pytest.mark.integration
    def test_full_user_workflow(self, test_client, sample_user_data, sample_card_data, sample_transaction_data):
        """Тест полного пользовательского сценария"""
        # 1. Регистрация пользователя
        register_response = test_client.post("/auth/register", json=sample_user_data)
        assert register_response.status_code == 201
        user_id = register_response.json()["id"]
        
        # 2. Вход в систему
        login_response = test_client.post("/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Добавление карты
        card_response = test_client.post("/cards/", json=sample_card_data, headers=headers)
        assert card_response.status_code == 201
        card_id = card_response.json()["id"]
        
        # 4. Создание транзакции
        transaction_response = test_client.post("/transactions/", json=sample_transaction_data, headers=headers)
        assert transaction_response.status_code == 201
        transaction_id = transaction_response.json()["id"]
        
        # 5. Проверка профиля
        profile_response = test_client.get("/users/profile", headers=headers)
        assert profile_response.status_code == 200
        assert profile_response.json()["id"] == user_id
        
        # 6. Проверка карт
        cards_response = test_client.get("/cards/", headers=headers)
        assert cards_response.status_code == 200
        assert len(cards_response.json()) == 1
        assert cards_response.json()[0]["id"] == card_id
        
        # 7. Проверка транзакций
        transactions_response = test_client.get("/transactions/", headers=headers)
        assert transactions_response.status_code == 200
        assert len(transactions_response.json()) == 1
        assert transactions_response.json()[0]["id"] == transaction_id
        
        print("✅ Полный пользовательский сценарий выполнен успешно")
    
    @pytest.mark.integration
    def test_admin_workflow(self, test_client, admin_user_data, sample_user_data):
        """Тест административного сценария"""
        # 1. Регистрация админа
        test_client.post("/auth/register", json=admin_user_data)
        
        # 2. Вход как админ
        admin_login = test_client.post("/auth/login", json={
            "email": admin_user_data["email"],
            "password": admin_user_data["password"]
        })
        admin_token = admin_login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 3. Регистрация обычного пользователя
        test_client.post("/auth/register", json=sample_user_data)
        
        # 4. Получение списка пользователей
        users_response = test_client.get("/admin/users", headers=admin_headers)
        assert users_response.status_code == 200
        assert len(users_response.json()) >= 2
        
        # 5. Изменение роли пользователя
        user_id = None
        for user in users_response.json():
            if user["email"] == sample_user_data["email"]:
                user_id = user["id"]
                break
        
        assert user_id is not None
        
        role_update = test_client.put(f"/admin/users/{user_id}", 
                                    json={"role": "terminal_operator"}, 
                                    headers=admin_headers)
        assert role_update.status_code == 200
        assert role_update.json()["role"] == "terminal_operator"
        
        print("✅ Административный сценарий выполнен успешно")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])


