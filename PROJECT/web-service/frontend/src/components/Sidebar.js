import React from 'react'
import './Sidebar.css'

const Sidebar = ({ currentPage, setCurrentPage }) => {
	const menuItems = [
		{ id: 'dashboard', icon: '▣', label: 'Главная' },
		{ id: 'cards', icon: '▤', label: 'Мои карты' },
		{ id: 'support', icon: '❓', label: 'Поддержка' },
		{ id: 'profile', icon: '👤', label: 'Профиль' },
		{ id: 'offer', icon: '§', label: 'Оферта' },
	]

	return (
		<div className='sidebar'>
			<div className='logo'>
				<div className='logo-icon'>PO</div>
				<div className='logo-text'>PayOk</div>
			</div>

			<nav className='nav-menu'>
				{menuItems.map(item => (
					<button
						key={item.id}
						className={`nav-item ${currentPage === item.id ? 'active' : ''}`}
						onClick={() => setCurrentPage(item.id)}
					>
						<span className='nav-icon' aria-hidden>
							{item.icon}
						</span>
						{item.label}
					</button>
				))}
			</nav>
		</div>
	)
}

export default Sidebar
