import React, { useState } from 'react'
import './App.css'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import Dashboard from './pages/Dashboard'
import Cards from './pages/Cards'
import Support from './pages/Support'
import Profile from './pages/Profile'
import Offer from './pages/Offer'

function App() {
	const [currentPage, setCurrentPage] = useState('dashboard')

	const renderPage = () => {
		switch (currentPage) {
			case 'dashboard':
				return <Dashboard />
			case 'cards':
				return <Cards />
			case 'support':
				return <Support />
			case 'profile':
				return <Profile />
			case 'offer':
				return <Offer />
			default:
				return <Dashboard />
		}
	}

	return (
		<div className='app-root'>
			<Sidebar currentPage={currentPage} setCurrentPage={setCurrentPage} />
			<main className='app-content'>
				<Header currentPage={currentPage} />
				{renderPage()}
			</main>
		</div>
	)
}

export default App
