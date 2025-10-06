// Основные переменные
let currentTheme = 'light'
let balanceVisible = true

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function () {
	initializeApp()
})

// Инициализация приложения
function initializeApp() {
	// Загружаем сохраненную тему
	const savedTheme = localStorage.getItem('paygo-theme')
	if (savedTheme) {
		setTheme(savedTheme)
		const themeToggle = document.getElementById('themeToggle')
		if (themeToggle) themeToggle.checked = savedTheme === 'dark'
	}

	// Проверяем сохраненные данные пользователя
	const token = localStorage.getItem('paygo-token')
	const fullName = localStorage.getItem('paygo-fullName')
	const phone = localStorage.getItem('paygo-phone')

	if (token && fullName) {
		updateAuthStatus(true)
		applyUserData(fullName, phone || '')
		unlockProtectedSections()
		showMainContent()
	} else {
		updateAuthStatus(false)
		showSiteInfo()
	}

	// Показываем главную страницу по умолчанию
	showPage('home')

	// Обновляем дату
	updateDate()
}

// Навигация по страницам
function showPage(pageName) {
	// Скрываем все страницы
	const pages = document.querySelectorAll('.page')
	pages.forEach(page => page.classList.remove('active'))

	// Показываем выбранную страницу
	const targetPage = document.getElementById(pageName)
	if (targetPage) {
		targetPage.classList.add('active')
	}

	// Обновляем активную ссылку в навигации
	updateActiveNavLink(pageName)
}

// Обновление активной ссылки в навигации
function updateActiveNavLink(pageName) {
	const navLinks = document.querySelectorAll('.nav-link')
	navLinks.forEach(link => link.classList.remove('active'))

	// Ищем ссылку, которая содержит showPage с нужным именем
	navLinks.forEach(link => {
		const onclick = link.getAttribute('onclick')
		if (onclick && onclick.includes(`showPage('${pageName}')`)) {
			link.classList.add('active')
		}
	})
}

// Переключение темы
function toggleTheme() {
	const themeToggle = document.getElementById('themeToggle')
	const newTheme = themeToggle && themeToggle.checked ? 'dark' : 'light'
	setTheme(newTheme)
	localStorage.setItem('paygo-theme', newTheme)
}

// Установка темы
function setTheme(theme) {
	currentTheme = theme
	document.documentElement.setAttribute('data-theme', theme)
}

// Сворачивание/разворачивание сайдбара
function toggleSidebar() {
	document.body.classList.toggle('sidebar-collapsed')
}

// Показать информацию о сайте
function showSiteInfo() {
	const siteInfo = document.getElementById('siteInfo')
	const mainContent = document.getElementById('mainContent')

	if (siteInfo) siteInfo.style.display = 'block'
	if (mainContent) mainContent.style.display = 'none'
}

// Показать основной контент
function showMainContent() {
	const siteInfo = document.getElementById('siteInfo')
	const mainContent = document.getElementById('mainContent')

	if (siteInfo) siteInfo.style.display = 'none'
	if (mainContent) mainContent.style.display = 'block'
}

// Обновление статуса авторизации
function updateAuthStatus(isLoggedIn) {
	const accountBtn = document.querySelector('.login-btn')
	if (accountBtn) {
		if (isLoggedIn) {
			const name = localStorage.getItem('paygo-fullName') || 'Пользователь'
			accountBtn.innerHTML = `<span class="login-icon">◉</span>${name}`
			accountBtn.onclick = logoutFromAccount
		} else {
			accountBtn.innerHTML = '<span class="login-icon">◎</span>Войти в аккаунт'
			accountBtn.onclick = showAccountModal
		}
	}
}

// Применить пользовательские данные на главной и в профиле
function applyUserData(fullName, phone) {
	// Приветствие
	const greeting = document.getElementById('greeting')
	if (greeting) greeting.textContent = `Здравствуйте, ${fullName}!`

	// Профиль
	const profileName = document.getElementById('profileFullName')
	const profilePhone = document.getElementById('profilePhone')
	if (profileName) profileName.value = fullName
	if (profilePhone) profilePhone.value = phone || ''
}

// Разблокировать защищенные секции (после входа)
function unlockProtectedSections() {
	// Скрыть заглушки “требуется регистрация”
	document
		.querySelectorAll('.registration-required')
		.forEach(el => (el.style.display = 'none'))
	// Показать контент
	const cardsContent = document.querySelector('.cards-content')
	if (cardsContent) cardsContent.style.display = 'block'
	const profileContent = document.querySelector('.profile-content')
	if (profileContent) profileContent.style.display = 'block'
}

// Регистрация без проверки и вход
function registerAndLogin() {
	const fullNameInput = document.getElementById('regFullName')
	const phoneInput = document.getElementById('regPhone')
	const fullName = fullNameInput ? fullNameInput.value.trim() : ''
	const phone = phoneInput ? phoneInput.value.trim() : ''

	if (!fullName || !phone) {
		alert('Введите ФИО и телефон')
		return
	}

	// Сохраняем и авторизуем
	localStorage.setItem('paygo-fullName', fullName)
	localStorage.setItem('paygo-phone', phone)
	localStorage.setItem('paygo-token', 'demo-token')

	applyUserData(fullName, phone)
	updateAuthStatus(true)
	unlockProtectedSections()

	// Показать основной контент на главной
	showPage('home')
	showMainContent()

	alert('Регистрация выполнена. Добро пожаловать!')
}

// Вход в аккаунт (демо)
function loginToAccount() {
	const login = document.getElementById('accountLogin').value
	const password = document.getElementById('accountPassword').value

	if (!login || !password) {
		alert('Пожалуйста, заполните все поля')
		return
	}

	// Демо-авторизация
	if (
		(login === 'demo' && password === 'demo') ||
		(login === 'developer' && password === 'paygo2025')
	) {
		localStorage.setItem('paygo-token', 'demo-token')
		// Если пользователь ранее регистрировался — применим данные
		const fullName = localStorage.getItem('paygo-fullName')
		const phone = localStorage.getItem('paygo-phone')
		if (fullName) applyUserData(fullName, phone || '')
		updateAuthStatus(true)
		unlockProtectedSections()
		closeAccountModal()
		showMainContent()
		alert('Добро пожаловать в PayGO!')
	} else {
		alert(
			'Неверные данные для входа. Попробуйте demo/demo или developer/paygo2025'
		)
	}
}

// Выход из аккаунта
function logoutFromAccount() {
	localStorage.removeItem('paygo-token')
	// Данные пользователя оставляем, чтобы показать в форме профиля при следующем входе при желании
	updateAuthStatus(false)
	// Вернем заглушки
	document
		.querySelectorAll('.registration-required')
		.forEach(el => (el.style.display = 'block'))
	const cardsContent = document.querySelector('.cards-content')
	if (cardsContent) cardsContent.style.display = 'none'
	const profileContent = document.querySelector('.profile-content')
	if (profileContent) profileContent.style.display = 'none'
	showSiteInfo()
	showPage('home')
	alert('Вы вышли из аккаунта')
}

// Показать модальное окно входа
function showAccountModal() {
	const modal = document.getElementById('accountModal')
	if (modal) {
		modal.style.display = 'block'
	}
}

// Закрыть модальное окно входа
function closeAccountModal() {
	const modal = document.getElementById('accountModal')
	if (modal) {
		modal.style.display = 'none'
	}
}

// Переключение видимости баланса
function toggleBalance() {
	balanceVisible = !balanceVisible
	const amount = document.querySelector('.amount')
	if (amount) {
		amount.textContent = balanceVisible ? '192 857.43 Р' : '••••••••••'
	}
}

// Обновление даты
function updateDate() {
	const dateElement = document.querySelector('.date')
	if (dateElement) {
		const now = new Date()
		const options = {
			weekday: 'long',
			year: 'numeric',
			month: 'long',
			day: 'numeric',
		}
		dateElement.textContent = now.toLocaleDateString('ru-RU', options)
	}
}

// Функции поддержки
function startChat() {
	// Открываем чат в новом окне
	const chatWindow = window.open('', 'PayOk Chat', 'width=400,height=600')
	if (chatWindow) {
		chatWindow.document.write(`
			<!DOCTYPE html>
			<html>
			<head>
				<title>Чат с поддержкой PayOk</title>
				<style>
					body { font-family: Arial; padding: 20px; background: #f5f5f5; }
					.chat-header { background: #ff6b35; color: white; padding: 15px; margin: -20px -20px 20px; }
					.chat-messages { background: white; padding: 15px; border-radius: 8px; min-height: 400px; }
					.chat-input { margin-top: 20px; display: flex; gap: 10px; }
					.chat-input input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
					.chat-input button { padding: 10px 20px; background: #ff6b35; color: white; border: none; border-radius: 5px; cursor: pointer; }
				</style>
			</head>
			<body>
				<div class="chat-header">
					<h2>💬 Чат с поддержкой</h2>
					<p>Мы онлайн и готовы помочь!</p>
				</div>
				<div class="chat-messages">
					<p><strong>Поддержка:</strong> Здравствуйте! Чем могу помочь?</p>
				</div>
				<div class="chat-input">
					<input type="text" placeholder="Введите сообщение..." />
					<button onclick="alert('Сообщение отправлено!')">Отправить</button>
				</div>
			</body>
			</html>
		`)
	}
}

function callBank() {
	// Открываем окно с информацией о звонке
	const callWindow = window.open('', 'PayOk Call', 'width=400,height=300')
	if (callWindow) {
		callWindow.document.write(`
			<!DOCTYPE html>
			<html>
			<head>
				<title>Звонок в банк</title>
				<style>
					body { font-family: Arial; padding: 30px; text-align: center; background: #f5f5f5; }
					.call-info { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
					.phone { font-size: 32px; font-weight: bold; color: #ff6b35; margin: 20px 0; }
					.btn { background: #ff6b35; color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-size: 16px; margin-top: 20px; }
				</style>
			</head>
			<body>
				<div class="call-info">
					<h2>📞 Звонок в банк</h2>
					<div class="phone">8-988-898-60-02</div>
					<p>График работы: Пн-Пт 9:00-21:00, Сб-Вс 10:00-18:00</p>
					<button class="btn" onclick="window.close()">Закрыть</button>
				</div>
			</body>
			</html>
		`)
	}
}

function sendEmail() {
	// Открываем окно для отправки email
	const emailWindow = window.open('', 'PayOk Email', 'width=500,height=400')
	if (emailWindow) {
		emailWindow.document.write(`
			<!DOCTYPE html>
			<html>
			<head>
				<title>Написать в поддержку</title>
				<style>
					body { font-family: Arial; padding: 30px; background: #f5f5f5; }
					.email-form { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
					h2 { color: #333; margin-bottom: 20px; }
					.form-group { margin-bottom: 15px; }
					label { display: block; margin-bottom: 5px; font-weight: 500; }
					input, textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-family: Arial; }
					textarea { min-height: 120px; resize: vertical; }
					.btn { background: #ff6b35; color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-size: 16px; width: 100%; margin-top: 10px; }
				</style>
			</head>
			<body>
				<div class="email-form">
					<h2>📧 Написать в поддержку</h2>
					<div class="form-group">
						<label>Ваш Email:</label>
						<input type="email" placeholder="example@mail.ru" />
					</div>
					<div class="form-group">
						<label>Тема:</label>
						<input type="text" placeholder="Опишите проблему кратко" />
					</div>
					<div class="form-group">
						<label>Сообщение:</label>
						<textarea placeholder="Опишите вашу проблему подробно..."></textarea>
					</div>
					<button class="btn" onclick="alert('Сообщение отправлено! Мы ответим в течение 24 часов.'); window.close()">Отправить</button>
				</div>
			</body>
			</html>
		`)
	}
}

// FAQ функции с отображением ответов
function toggleFAQ(item) {
	item.classList.toggle('expanded')

	// Проверяем, есть ли уже ответ
	let answer = item.nextElementSibling
	if (!answer || !answer.classList.contains('faq-answer')) {
		// Создаём ответ
		answer = document.createElement('div')
		answer.className = 'faq-answer'

		const question = item.querySelector('span').textContent

		// Определяем ответ по вопросу
		if (question.includes('карту')) {
			answer.innerHTML = `
				<p><strong>Чтобы добавить новую карту:</strong></p>
				<ol>
					<li>Перейдите в раздел "Мои карты" в меню</li>
					<li>Нажмите кнопку "+ Добавить карту"</li>
					<li>Введите номер карты, срок действия и CVV</li>
					<li>Подтвердите добавление через SMS-код</li>
				</ol>
				<p>Все данные карты надёжно шифруются и защищены.</p>
			`
		} else if (question.includes('пароль')) {
			answer.innerHTML = `
				<p><strong>Для смены пароля:</strong></p>
				<ol>
					<li>Откройте раздел "Профиль"</li>
					<li>Нажмите "Безопасность"</li>
					<li>Выберите "Сменить пароль"</li>
					<li>Введите текущий и новый пароль</li>
					<li>Подтвердите изменения</li>
				</ol>
				<p>Рекомендуем использовать надёжный пароль (минимум 8 символов, буквы и цифры).</p>
			`
		} else if (question.includes('уведомления')) {
			answer.innerHTML = `
				<p><strong>Настройка уведомлений:</strong></p>
				<ol>
					<li>Перейдите в "Профиль"</li>
					<li>Откройте вкладку "Уведомления"</li>
					<li>Выберите типы уведомлений:
						<ul>
							<li>Push-уведомления</li>
							<li>SMS-уведомления</li>
							<li>Email-уведомления</li>
						</ul>
					</li>
					<li>Сохраните изменения</li>
				</ol>
			`
		}

		item.parentNode.insertBefore(answer, item.nextSibling)
	}

	// Показываем/скрываем ответ
	if (item.classList.contains('expanded')) {
		answer.style.display = 'block'
	} else {
		answer.style.display = 'none'
	}
}

// Функции переводов
function executeTransfer() {
	alert('Перевод выполнен успешно!')
}

// Функции платежей
function showQRPayment() {
	alert('Открывается QR-код для оплаты')
}
function showSBPPayment() {
	alert('Открывается форма СБП платежа')
}
function showBiometricPayment() {
	alert('Начинается биометрическая аутентификация')
}
function showCardPayment() {
	alert('Открывается форма оплаты картой')
}
function selectPayment(type) {
	alert(`Выбрана категория: ${type}`)
}

// Функции истории
function transferToFavorite(id) {
	alert(`Перевод избранному контакту ${id}`)
}

// Функции оферты
function showOffer() {
	const modal = document.getElementById('offerModal')
	if (modal) {
		// Контент уже в HTML, просто показать
		modal.style.display = 'block'
	}
}

function closeOffer() {
	const modal = document.getElementById('offerModal')
	if (modal) {
		modal.style.display = 'none'
	}
}

function showPrivacy() {
	alert('Открывается политика конфиденциальности')
}

function showRegister() {
	showPage('register')
}

function forgotPassword() {
	alert('Функция восстановления пароля будет доступна позже')
}

// Функции оферты на странице
function acceptOffer() {
	const checkbox = document.getElementById('offerCheckbox')
	if (checkbox && checkbox.checked) {
		localStorage.setItem('paygo-offer-accepted', 'true')
		alert('✅ Оферта принята! Спасибо за использование PayOk.')
		showPage('home')
	}
}

function downloadOffer() {
	alert('📄 Скачивание PDF-версии оферты... (функция в разработке)')
}

// Обработчик чекбокса оферты
document.addEventListener('DOMContentLoaded', function () {
	const checkbox = document.getElementById('offerCheckbox')
	const acceptBtn = document.getElementById('acceptBtn')

	if (checkbox && acceptBtn) {
		checkbox.addEventListener('change', function () {
			acceptBtn.disabled = !this.checked
		})
	}
})

// Функция добавления новой карты
function addNewCard() {
	const cardWindow = window.open('', 'Add Card', 'width=500,height=600')
	if (cardWindow) {
		cardWindow.document.write(`
			<!DOCTYPE html>
			<html>
			<head>
				<title>Добавить карту</title>
				<style>
					body { font-family: Arial; padding: 30px; background: #f5f5f5; }
					.card-form { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
					h2 { color: #333; margin-bottom: 20px; }
					.form-group { margin-bottom: 20px; }
					label { display: block; margin-bottom: 8px; font-weight: 500; color: #333; }
					input { width: 100%; padding: 12px; border: 2px solid #e9ecef; border-radius: 8px; font-size: 16px; }
					input:focus { outline: none; border-color: #ff6b35; }
					.card-preview { background: linear-gradient(135deg, #ff6b35, #e55a2b); color: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; }
					.preview-number { font-size: 20px; letter-spacing: 2px; margin-bottom: 10px; }
					.btn { background: #ff6b35; color: white; border: none; padding: 14px; border-radius: 8px; cursor: pointer; font-size: 16px; width: 100%; font-weight: 600; }
					.btn:hover { background: #e55a2b; }
				</style>
			</head>
			<body>
				<div class="card-form">
					<h2>💳 Добавление новой карты</h2>
					
					<div class="card-preview">
						<div class="preview-number" id="previewNumber">•••• •••• •••• ••••</div>
						<div>Срок действия: <span id="previewExpiry">ММ/ГГ</span></div>
					</div>
					
					<div class="form-group">
						<label>Номер карты:</label>
						<input type="text" id="cardNumber" placeholder="1234 5678 9012 3456" maxlength="19" oninput="formatCardNumber(this)" />
					</div>
					
					<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
						<div class="form-group">
							<label>Срок действия:</label>
							<input type="text" id="cardExpiry" placeholder="ММ/ГГ" maxlength="5" oninput="formatExpiry(this)" />
						</div>
						<div class="form-group">
							<label>CVV:</label>
							<input type="text" id="cardCVV" placeholder="123" maxlength="3" />
						</div>
					</div>
					
					<div class="form-group">
						<label>Имя держателя:</label>
						<input type="text" id="cardHolder" placeholder="IVAN IVANOV" style="text-transform: uppercase;" />
					</div>
					
					<button class="btn" onclick="saveCard()">Добавить карту</button>
				</div>
				
				<script>
					function formatCardNumber(input) {
						let value = input.value.replace(/\\s/g, '').replace(/[^0-9]/g, '');
						let formatted = value.match(/.{1,4}/g)?.join(' ') || value;
						input.value = formatted;
						document.getElementById('previewNumber').textContent = formatted || '•••• •••• •••• ••••';
					}
					
					function formatExpiry(input) {
						let value = input.value.replace(/[^0-9]/g, '');
						if (value.length >= 2) {
							value = value.slice(0,2) + '/' + value.slice(2,4);
						}
						input.value = value;
						document.getElementById('previewExpiry').textContent = value || 'ММ/ГГ';
					}
					
					function saveCard() {
						const number = document.getElementById('cardNumber').value;
						const expiry = document.getElementById('cardExpiry').value;
						const cvv = document.getElementById('cardCVV').value;
						const holder = document.getElementById('cardHolder').value;
						
						if (!number || !expiry || !cvv || !holder) {
							alert('Пожалуйста, заполните все поля');
							return;
						}
						
						alert('✅ Карта успешно добавлена!\\n\\nДля безопасности мы отправили SMS-код на ваш номер телефона.');
						window.close();
					}
				</script>
			</body>
			</html>
		`)
	}
}

// Закрытие модальных окон при клике вне их
window.onclick = function (event) {
	const modals = document.querySelectorAll('.modal')
	modals.forEach(modal => {
		if (event.target === modal) {
			modal.style.display = 'none'
		}
	})
}
