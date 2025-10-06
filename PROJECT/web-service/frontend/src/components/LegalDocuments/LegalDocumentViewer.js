import React, { useState, useEffect } from 'react';
import { Card, Button, Spin, Alert, Tag, Space, Typography, Divider } from 'antd';
import { CheckCircleOutlined, FileTextOutlined, ClockCircleOutlined } from '@ant-design/icons';
import axios from 'axios';
import './LegalDocumentViewer.css';

const { Title, Text, Paragraph } = Typography;

const LegalDocumentViewer = ({ documentType, onAccept, showAcceptButton = true }) => {
    const [document, setDocument] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [accepting, setAccepting] = useState(false);

    useEffect(() => {
        fetchDocument();
    }, [documentType]);

    const fetchDocument = async () => {
        try {
            setLoading(true);
            const response = await axios.get(`/api/legal/documents/${documentType}`);
            setDocument(response.data);
            setError(null);
        } catch (err) {
            setError('Ошибка загрузки документа');
            console.error('Error fetching document:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleAccept = async () => {
        if (!document) return;
        
        try {
            setAccepting(true);
            await axios.post('/api/legal/user/accept', {
                document_id: document.id
            });
            
            if (onAccept) {
                onAccept(document.id);
            }
            
            // Показываем уведомление об успешном принятии
            // Здесь можно добавить toast уведомление
        } catch (err) {
            setError('Ошибка принятия документа');
            console.error('Error accepting document:', err);
        } finally {
            setAccepting(false);
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
            <div className="legal-document-loading">
                <Spin size="large" />
                <Text>Загрузка документа...</Text>
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
                    <Button size="small" onClick={fetchDocument}>
                        Попробовать снова
                    </Button>
                }
            />
        );
    }

    if (!document) {
        return (
            <Alert
                message="Документ не найден"
                description="Запрашиваемый документ не найден или неактивен"
                type="warning"
                showIcon
            />
        );
    }

    return (
        <div className="legal-document-viewer">
            <Card className="legal-document-card">
                <div className="document-header">
                    <Space direction="vertical" size="small" style={{ width: '100%' }}>
                        <div className="document-title-section">
                            <Title level={2} className="document-title">
                                <FileTextOutlined /> {document.title}
                            </Title>
                            <Space size="middle">
                                <Tag color={getDocumentTypeColor(document.type)}>
                                    {getDocumentTypeLabel(document.type)}
                                </Tag>
                                <Tag color="blue">
                                    Версия {document.version}
                                </Tag>
                                {document.requires_acceptance && (
                                    <Tag color="orange" icon={<ClockCircleOutlined />}>
                                        Требует принятия
                                    </Tag>
                                )}
                            </Space>
                        </div>
                        
                        <div className="document-meta">
                            <Space size="large">
                                <Text type="secondary">
                                    <ClockCircleOutlined /> Дата вступления в силу: {new Date(document.effective_date).toLocaleDateString('ru-RU')}
                                </Text>
                                <Text type="secondary">
                                    <ClockCircleOutlined /> Обновлено: {new Date(document.updated_at).toLocaleDateString('ru-RU')}
                                </Text>
                            </Space>
                        </div>
                    </Space>
                </div>

                <Divider />

                <div className="document-content">
                    <div 
                        className="document-html-content"
                        dangerouslySetInnerHTML={{ __html: document.content }}
                    />
                </div>

                {showAcceptButton && document.requires_acceptance && (
                    <div className="document-actions">
                        <Divider />
                        <div className="accept-section">
                            <Alert
                                message="Принятие документа"
                                description="Для продолжения работы с системой необходимо принять условия данного документа"
                                type="info"
                                showIcon
                                style={{ marginBottom: 16 }}
                            />
                            <Button
                                type="primary"
                                size="large"
                                icon={<CheckCircleOutlined />}
                                onClick={handleAccept}
                                loading={accepting}
                                className="accept-button"
                            >
                                Принять условия
                            </Button>
                            <Text type="secondary" style={{ display: 'block', marginTop: 8 }}>
                                Нажимая кнопку "Принять условия", вы соглашаетесь с содержанием документа
                            </Text>
                        </div>
                    </div>
                )}
            </Card>
        </div>
    );
};

export default LegalDocumentViewer;
