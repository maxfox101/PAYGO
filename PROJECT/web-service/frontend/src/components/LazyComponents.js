import React, { Suspense, lazy } from 'react';
import { Spin, Alert, Button } from 'antd';
import { LoadingOutlined, ExclamationCircleOutlined } from '@ant-design/icons';

// Компонент загрузки с анимацией
const LoadingSpinner = ({ size = 'large', text = 'Загрузка...' }) => (
  <div style={{ 
    display: 'flex', 
    flexDirection: 'column', 
    alignItems: 'center', 
    justifyContent: 'center', 
    padding: '40px',
    minHeight: '200px'
  }}>
    <Spin 
      size={size} 
      indicator={<LoadingOutlined style={{ fontSize: 24 }} spin />} 
    />
    <div style={{ marginTop: '16px', color: '#666' }}>{text}</div>
  </div>
);

// Компонент ошибки с возможностью повтора
const ErrorFallback = ({ error, resetErrorBoundary }) => (
  <div style={{ 
    display: 'flex', 
    flexDirection: 'column', 
    alignItems: 'center', 
    justifyContent: 'center', 
    padding: '40px',
    minHeight: '200px',
    textAlign: 'center'
  }}>
    <ExclamationCircleOutlined style={{ fontSize: 48, color: '#ff4d4f', marginBottom: '16px' }} />
    <h3 style={{ color: '#ff4d4f', marginBottom: '16px' }}>Что-то пошло не так</h3>
    <p style={{ color: '#666', marginBottom: '24px', maxWidth: '400px' }}>
      Произошла ошибка при загрузке компонента. Попробуйте обновить страницу или повторить попытку.
    </p>
    <Button type="primary" onClick={resetErrorBoundary}>
      Повторить попытку
    </Button>
    <div style={{ marginTop: '16px' }}>
      <details style={{ textAlign: 'left' }}>
        <summary style={{ cursor: 'pointer', color: '#666' }}>Детали ошибки</summary>
        <pre style={{ 
          background: '#f5f5f5', 
          padding: '12px', 
          borderRadius: '4px', 
          marginTop: '8px',
          fontSize: '12px',
          overflow: 'auto',
          maxWidth: '100%'
        }}>
          {error.message}
        </pre>
      </details>
    </div>
  </div>
);

// Error Boundary для обработки ошибок в lazy компонентах
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error Boundary caught an error:', error, errorInfo);
    // Здесь можно отправить ошибку в систему мониторинга
  }

  resetError = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <ErrorFallback 
          error={this.state.error} 
          resetErrorBoundary={this.resetError} 
        />
      );
    }

    return this.props.children;
  }
}

// HOC для добавления Error Boundary к lazy компонентам
const withErrorBoundary = (Component) => {
  return (props) => (
    <ErrorBoundary>
      <Component {...props} />
    </ErrorBoundary>
  );
};

// HOC для добавления Suspense к lazy компонентам
const withSuspense = (Component, fallback = null) => {
  const SuspenseComponent = (props) => (
    <Suspense fallback={fallback || <LoadingSpinner />}>
      <Component {...props} />
    </Suspense>
  );
  
  return withErrorBoundary(SuspenseComponent);
};

// Lazy компоненты для основных страниц
export const LazyDashboard = withSuspense(
  lazy(() => import('../pages/Dashboard')),
  <LoadingSpinner text="Загрузка дашборда..." />
);

export const LazyCards = withSuspense(
  lazy(() => import('../pages/Cards')),
  <LoadingSpinner text="Загрузка карт..." />
);

export const LazyProfile = withSuspense(
  lazy(() => import('../pages/Profile')),
  <LoadingSpinner text="Загрузка профиля..." />
);

export const LazySupport = withSuspense(
  lazy(() => import('../pages/Support')),
  <LoadingSpinner text="Загрузка поддержки..." />
);

// Lazy компоненты для модальных окон
export const LazyCardModal = withSuspense(
  lazy(() => import('./CardModal')),
  <LoadingSpinner text="Загрузка карты..." />
);

export const LazyTransactionModal = withSuspense(
  lazy(() => import('./TransactionModal')),
  <LoadingSpinner text="Загрузка транзакции..." />
);

export const LazySettingsModal = withSuspense(
  lazy(() => import('./SettingsModal')),
  <LoadingSpinner text="Загрузка настроек..." />
);

// Lazy компоненты для форм
export const LazyLoginForm = withSuspense(
  lazy(() => import('./LoginForm')),
  <LoadingSpinner text="Загрузка формы входа..." />
);

export const LazyRegistrationForm = withSuspense(
  lazy(() => import('./RegistrationForm')),
  <LoadingSpinner text="Загрузка формы регистрации..." />
);

export const LazyPasswordResetForm = withSuspense(
  lazy(() => import('./PasswordResetForm')),
  <LoadingSpinner text="Загрузка формы сброса пароля..." />
);

// Lazy компоненты для административных функций
export const LazyAdminPanel = withSuspense(
  lazy(() => import('./AdminPanel')),
  <LoadingSpinner text="Загрузка панели администратора..." />
);

export const LazyUserManagement = withSuspense(
  lazy(() => import('./UserManagement')),
  <LoadingSpinner text="Загрузка управления пользователями..." />
);

export const LazyTerminalManagement = withSuspense(
  lazy(() => import('./TerminalManagement')),
  <LoadingSpinner text="Загрузка управления терминалами..." />
);

export const LazyTransactionHistory = withSuspense(
  lazy(() => import('./TransactionHistory')),
  <LoadingSpinner text="Загрузка истории транзакций..." />
);

// Lazy компоненты для аналитики и отчетов
export const LazyAnalytics = withSuspense(
  lazy(() => import('./Analytics')),
  <LoadingSpinner text="Загрузка аналитики..." />
);

export const LazyReports = withSuspense(
  lazy(() => import('./Reports')),
  <LoadingSpinner text="Загрузка отчетов..." />
);

export const LazyCharts = withSuspense(
  lazy(() => import('./Charts')),
  <LoadingSpinner text="Загрузка графиков..." />
);

// Lazy компоненты для уведомлений
export const LazyNotifications = withSuspense(
  lazy(() => import('./Notifications')),
  <LoadingSpinner text="Загрузка уведомлений..." />
);

export const LazyNotificationSettings = withSuspense(
  lazy(() => import('./NotificationSettings')),
  <LoadingSpinner text="Загрузка настроек уведомлений..." />
);

// Lazy компоненты для безопасности
export const LazySecuritySettings = withSuspense(
  lazy(() => import('./SecuritySettings')),
  <LoadingSpinner text="Загрузка настроек безопасности..." />
);

export const LazyTwoFactorSetup = withSuspense(
  lazy(() => import('./TwoFactorSetup')),
  <LoadingSpinner text="Загрузка настройки двухфакторной аутентификации..." />
);

// Lazy компоненты для платежей
export const LazyPaymentForm = withSuspense(
  lazy(() => import('./PaymentForm')),
  <LoadingSpinner text="Загрузка формы платежа..." />
);

export const LazyPaymentHistory = withSuspense(
  lazy(() => import('./PaymentHistory')),
  <LoadingSpinner text="Загрузка истории платежей..." />
);

export const LazyPaymentMethods = withSuspense(
  lazy(() => import('./PaymentMethods')),
  <LoadingSpinner text="Загрузка способов оплаты..." />
);

// Lazy компоненты для терминалов
export const LazyTerminalStatus = withSuspense(
  lazy(() => import('./TerminalStatus')),
  <LoadingSpinner text="Загрузка статуса терминала..." />
);

export const LazyTerminalMap = withSuspense(
  lazy(() => import('./TerminalMap')),
  <LoadingSpinner text="Загрузка карты терминалов..." />
);

// Компонент для предзагрузки важных компонентов
export const PreloadManager = () => {
  React.useEffect(() => {
    // Предзагрузка критически важных компонентов
    const preloadCriticalComponents = async () => {
      try {
        // Предзагружаем основные страницы
        await Promise.all([
          import('../pages/Dashboard'),
          import('../pages/Cards'),
          import('../pages/Profile'),
          import('./LoginForm'),
          import('./CardModal')
        ]);
      } catch (error) {
        console.warn('Preloading failed:', error);
      }
    };

    // Запускаем предзагрузку после загрузки основного контента
    const timer = setTimeout(preloadCriticalComponents, 2000);
    return () => clearTimeout(timer);
  }, []);

  return null;
};

// Хук для управления lazy loading
export const useLazyLoading = (importFunc, dependencies = []) => {
  const [Component, setComponent] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    let mounted = true;

    const loadComponent = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const module = await importFunc();
        const ComponentToLoad = module.default || module;
        
        if (mounted) {
          setComponent(() => ComponentToLoad);
          setLoading(false);
        }
      } catch (err) {
        if (mounted) {
          setError(err);
          setLoading(false);
        }
      }
    };

    loadComponent();

    return () => {
      mounted = false;
    };
  }, dependencies);

  return { Component, loading, error };
};

// Компонент для условного рендеринга с lazy loading
export const ConditionalLazyComponent = ({ 
  condition, 
  importFunc, 
  fallback = null,
  errorFallback = null,
  ...props 
}) => {
  const { Component, loading, error } = useLazyLoading(importFunc, [condition]);

  if (!condition) {
    return null;
  }

  if (loading) {
    return fallback || <LoadingSpinner />;
  }

  if (error) {
    return errorFallback || <ErrorFallback error={error} />;
  }

  return Component ? <Component {...props} /> : null;
};

// Экспорт основных компонентов
export {
  LoadingSpinner,
  ErrorFallback,
  ErrorBoundary,
  withErrorBoundary,
  withSuspense
};
