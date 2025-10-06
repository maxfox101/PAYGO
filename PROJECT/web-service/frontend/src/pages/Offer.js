import React, { useState } from 'react'

const sections = [
	{
		title: '1. Общие положения',
		text: 'Настоящая публичная оферта (далее — Оферта) является официальным предложением сервиса PayOk любому дееспособному лицу заключить договор на условиях, изложенных ниже.',
	},
	{
		title: '2. Предмет договора',
		text: 'Сервис предоставляет пользователю доступ к личному кабинету, управлению картами и оплате услуг. Пользователь обязуется соблюдать правила использования сервиса.',
	},
	{
		title: '3. Регистрация и доступ',
		text: 'Для использования сервиса требуется регистрация и подтверждение контактов. Пользователь несет ответственность за сохранность учетных данных.',
	},
	{
		title: '4. Платежи и комиссии',
		text: 'Оплата осуществляется через подключенных партнеров-эквайеров. Возможны комиссии в соответствии с тарифами партнеров.',
	},
	{
		title: '5. Персональные данные',
		text: 'Обработка персональных данных осуществляется в соответствии с Политикой конфиденциальности и действующим законодательством.',
	},
	{
		title: '6. Ответственность',
		text: 'Сервис не несет ответственность за перебои связи, действия третьих лиц и форс-мажор. Пользователь обязуется использовать сервис добросовестно.',
	},
	{
		title: '7. Заключительные положения',
		text: 'Оферта может быть изменена с уведомлением на сайте. Продолжение использования означает согласие с обновленными условиями.',
	},
]

export default function Offer() {
	const [accepted, setAccepted] = useState(false)

	return (
		<div className='card' style={{ maxWidth: 960, margin: '0 auto' }}>
			<h1 style={{ marginTop: 0 }}>Публичная оферта PayOk</h1>
			<p className='text-muted'>Версия 1.0 · Дата публикации: 05.10.2025</p>
			<div className='separator' />

			<div>
				{sections.map((s, i) => (
					<section key={i} style={{ marginBottom: 16 }}>
						<h3 style={{ margin: '8px 0' }}>{s.title}</h3>
						<p style={{ margin: 0 }}>{s.text}</p>
					</section>
				))}
			</div>

			<div className='separator' />

			<label
				style={{
					display: 'flex',
					alignItems: 'center',
					gap: 8,
					marginBottom: 12,
				}}
			>
				<input
					type='checkbox'
					checked={accepted}
					onChange={e => setAccepted(e.target.checked)}
				/>
				<span>Я прочитал(а) и принимаю условия публичной оферты</span>
			</label>

			<div style={{ display: 'flex', gap: 12 }}>
				<button
					className='btn'
					disabled={!accepted}
					onClick={() => alert('Оферта принята')}
				>
					Принять
				</button>
				<a
					className='btn'
					href='#top'
					onClick={e => e.preventDefault()}
					style={{
						background: 'transparent',
						color: 'var(--brand-orange)',
						borderColor: 'var(--brand-orange)',
					}}
				>
					Скачать PDF
				</a>
			</div>
		</div>
	)
}

