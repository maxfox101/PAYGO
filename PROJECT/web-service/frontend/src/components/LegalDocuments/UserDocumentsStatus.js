import React, { useState, useEffect } from 'react';
import { Card, List, Tag, Button, Space, Typography, Progress, Alert, Spin } from 'antd';
import { 
    CheckCircleOutlined, 
    ClockCircleOutlined, 
    FileTextOutlined,
    ExclamationCircleOutlined,
    InfoCircleOutlined
} from '@ant-design/icons';
import axios from 'axios';
import './UserDocumentsStatus.css';

const { Title, Text, Paragraph } = Typography;

const UserDocumentsStatus = ({ onDocumentClick }) => {
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchUserDocumentsStatus();
    }, []);

    const fetchUserDocumentsStatus = async () => {
        try {
            setLoading(true);
            const response = await axios.get('/api/legal/user/status');
            setStatus(response.data);
            setError(null);
        } catch (err) {
            setError('Ошибка загрузки статуса документов');
            console.error('Error fetching user documents status:', err);
        } finally {
            setLoading(false);
        }
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'accepted':
                return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
            case 'pending':
                return <ClockCircleOutlined style={{ color: '#faad14' }} />;
            case 'not_required':
                return <InfoCircleOutlined style={{ color: '#1890ff' }} />;
            default:
                return <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />;
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'accepted':
                return 'success';
            case 'pending':
                return 'warning';
            case 'not_required':
                return 'default';
            default:
                return 'error';
        }
    };

    const getStatusText = (status) => {
        switch (status) {
            case 'accepted':
                return 'Принят';
            case 'pending':
                return 'Ожидает принятия';
            case 'not_required':
                return 'Не требуется';
            default:
                return 'Неизвестно';
        }
    };

    const getDocumentTypeLabel = (type) => {
        const labels = {
            'offer': 'Публичная оферта',
            'terms': 'Условия использования',
            'privacy': 'Политика конфиденциальности',
            'agreement': 'Пользовательское соглашение'
        };
        return labels[type] || type;
    };

    const getDocumentTypeColor = (type) => {
        const colors = {
            'offer': 'red',
            'terms': 'blue',
            'privacy': 'green',
            'agreement': 'orange'
        };
        return colors[type] || 'default';
    };

    if (loading) {
        return (
            <div className="user-documents-status-loading">
                <Spin size="large" />
                <Text>Загрузка статуса документов...</Text>
            </div>
        );
    }

    if (error) {
        return (
            <Alert
                message="Ошибка"
                description={error}
                type="error"
                showIcon
                action={
                    <Button size="small" onClick={fetchUserDocumentsStatus}>
                        Попробовать снова
                    </Button>
                }
            />
        );
    }

    if (!status) {
        return (
            <Alert
                message="Статус не найден"
                description="Не удалось получить статус документов"
                type="warning"
                showIcon
            />
        );
    }

    const pendingCount = status.pending_documents;
    const totalRequired = status.documents.filter(doc => doc.status === 'pending' || doc.status === 'accepted').length;
    const completionPercentage = totalRequired > 0 ? Math.round((status.accepted_documents / totalRequired) * 100) : 100;

    return (
        <div className="user-documents-status">
            <Card className="status-overview-card">
                <div className="status-header">
                    <Title level={3}>
                        <FileTextOutlined /> Статус правовых документов
                    </Title>
                    <div className="completion-info">
                        <Progress 
                            type="circle" 
                            percent={completionPercentage}
                            size={80}
                            strokeColor={completionPercentage === 100 ? '#52c41a' : '#faad14'}
                            format={percent => `${percent}%`}
                        />
                        <div className="completion-text">
                            <Text strong>Завершено</Text>
                            <Text type="secondary">
                                {status.accepted_documents} из {totalRequired} документов
                            </Text>
                        </div>
                    </div>
                </div>

                {pendingCount > 0 && (
                    <Alert
                        message="Требуется внимание"
                        description={`У вас есть ${pendingCount} документ(ов), требующих принятия для продолжения работы с системой`}
                        type="warning"
                        showIcon
                        style={{ marginBottom: 16 }}
                        action={
                            <Button size="small" type="primary">
                                Просмотреть
                            </Button>
                        }
                    />
                )}

                <div className="status-summary">
                    <Space size="large">
                        <div className="summary-item">
                            <Text strong>Всего документов:</Text>
                            <Tag color="blue">{status.total_documents}</Tag>
                        </div>
                        <div className="summary-item">
                            <Text strong>Принято:</Text>
                            <Tag color="success">{status.accepted_documents}</Tag>
                        </div>
                        <div className="summary-item">
                            <Text strong>Ожидает принятия:</Text>
                            <Tag color="warning">{status.pending_documents}</Tag>
                        </div>
                    </Space>
                </div>
            </Card>

            <Card 
                title="Список документов" 
                className="documents-list-card"
                style={{ marginTop: 16 }}
            >
                <List
                    dataSource={status.documents}
                    renderItem={(doc) => (
                        <List.Item
                            className={`document-list-item document-status-${doc.status}`}
                            actions={[
                                doc.status === 'pending' && (
                                    <Button 
                                        type="primary" 
                                        size="small"
                                        onClick={() => onDocumentClick && onDocumentClick(doc.type)}
                                    >
                                        Принять
                                    </Button>
                                ),
                                doc.status === 'accepted' && (
                                    <Button 
                                        type="link" 
                                        size="small"
                                        onClick={() => onDocumentClick && onDocumentClick(doc.type)}
                                    >
                                        Просмотреть
                                    </Button>
                                )
                            ].filter(Boolean)}
                        >
                            <List.Item.Meta
                                avatar={getStatusIcon(doc.status)}
                                title={
                                    <Space>
                                        <Text strong>{doc.title}</Text>
                                        <Tag color={getDocumentTypeColor(doc.type)}>
                                            {getDocumentTypeLabel(doc.type)}
                                        </Tag>
                                        <Tag color={getStatusColor(doc.status)}>
                                            {getStatusText(doc.status)}
                                        </Tag>
                                    </Space>
                                }
                                description={
                                    <Space direction="vertical" size="small">
                                        <Text type="secondary">
                                            Версия {doc.version} • Вступил в силу {new Date(doc.effective_date).toLocaleDateString('ru-RU')}
                                        </Text>
                                        {doc.status === 'accepted' && (
                                            <Text type="success" style={{ fontSize: '12px' }}>
                                                ✓ Принят пользователем
                                            </Text>
                                        )}
                                        {doc.status === 'pending' && (
                                            <Text type="warning" style={{ fontSize: '12px' }}>
                                                ⚠ Требует принятия для продолжения работы
                                            </Text>
                                        )}
                                    </Space>
                                }
                            />
                        </List.Item>
                    )}
                />
            </Card>
        </div>
    );
};

export default UserDocumentsStatus;
