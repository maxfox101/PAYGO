import React from 'react'
import { useAuth } from '../context/AuthContext'
import './Header.css'

const Header = ({ currentPage }) => {
	const { user } = useAuth()

	const pageConfig = {
		dashboard: { greeting: 'Сегодня', title: 'Главная', showBalance: true },
		cards: {
			greeting: 'Управление картами',
			title: 'Мои карты',
			showBalance: false,
		},
		support: {
			greeting: 'Нужна помощь?',
			title: 'Поддержка',
			showBalance: false,
		},
		profile: {
			greeting: 'Личные данные',
			title: 'Профиль',
			showBalance: false,
		},
		offer: {
			greeting: 'Правовые документы',
			title: 'Публичная оферта',
			showBalance: false,
		},
	}

	const config = pageConfig[currentPage] || pageConfig.dashboard

	return (
		<div className='header'>
			<div>
				<div className='greeting'>{config.greeting}</div>
				<h1 className='page-title'>{config.title}</h1>
			</div>
			{config.showBalance && (
				<div className='user-info'>
					<div className='balance'>
						<div className='balance-amount'>192 857.43 ₽</div>
						<div className='balance-label'>Общий баланс</div>
					</div>
				</div>
			)}
		</div>
	)
}

export default Header
