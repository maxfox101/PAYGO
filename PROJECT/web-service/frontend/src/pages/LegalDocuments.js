import React, { useState } from 'react';
import { Tabs, Card, Typography, Space, Button, Modal } from 'antd';
import { 
    FileTextOutlined, 
    CheckCircleOutlined, 
    ExclamationCircleOutlined,
    InfoCircleOutlined
} from '@ant-design/icons';
import LegalDocumentViewer from '../components/LegalDocuments/LegalDocumentViewer';
import UserDocumentsStatus from '../components/LegalDocuments/UserDocumentsStatus';
import './LegalDocuments.css';

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;

const LegalDocuments = () => {
    const [activeTab, setActiveTab] = useState('status');
    const [selectedDocument, setSelectedDocument] = useState(null);
    const [isModalVisible, setIsModalVisible] = useState(false);

    const handleDocumentClick = (documentType) => {
        setSelectedDocument(documentType);
        setActiveTab('viewer');
    };

    const handleDocumentAccept = (documentId) => {
        // Обновляем статус после принятия документа
        setActiveTab('status');
        // Можно добавить уведомление об успешном принятии
    };

    const showDocumentModal = (documentType) => {
        setSelectedDocument(documentType);
        setIsModalVisible(true);
    };

    const handleModalOk = () => {
        setIsModalVisible(false);
        setSelectedDocument(null);
    };

    const handleModalCancel = () => {
        setIsModalVisible(false);
        setSelectedDocument(null);
    };

    const documentTypes = [
        { key: 'offer', label: 'Публичная оферта', icon: <FileTextOutlined />, color: 'red' },
        { key: 'terms', label: 'Условия использования', icon: <FileTextOutlined />, color: 'blue' },
        { key: 'privacy', label: 'Политика конфиденциальности', icon: <FileTextOutlined />, color: 'green' },
        { key: 'agreement', label: 'Пользовательское соглашение', icon: <FileTextOutlined />, color: 'orange' }
    ];

    return (
        <div className="legal-documents-page">
            <div className="page-header">
                <Title level={2}>
                    <FileTextOutlined /> Правовые документы
                </Title>
                <Paragraph>
                    Ознакомьтесь с правовыми документами системы PayGo и примите необходимые условия для продолжения работы
                </Paragraph>
            </div>

            <Card className="main-content-card">
                <Tabs 
                    activeKey={activeTab} 
                    onChange={setActiveTab}
                    className="legal-documents-tabs"
                >
                    <TabPane 
                        tab={
                            <span>
                                <CheckCircleOutlined /> Статус документов
                            </span>
                        } 
                        key="status"
                    >
                        <UserDocumentsStatus onDocumentClick={handleDocumentClick} />
                    </TabPane>

                    <TabPane 
                        tab={
                            <span>
                                <FileTextOutlined /> Просмотр документов
                            </span>
                        } 
                        key="viewer"
                    >
                        <div className="document-selector">
                            <Title level={4}>Выберите документ для просмотра:</Title>
                            <Space wrap size="middle">
                                {documentTypes.map(doc => (
                                    <Button
                                        key={doc.key}
                                        type={selectedDocument === doc.key ? 'primary' : 'default'}
                                        icon={doc.icon}
                                        size="large"
                                        onClick={() => setSelectedDocument(doc.key)}
                                        style={{ 
                                            borderColor: doc.color,
                                            color: selectedDocument === doc.key ? '#fff' : doc.color
                                        }}
                                    >
                                        {doc.label}
                                    </Button>
                                ))}
                            </Space>
                        </div>

                        {selectedDocument && (
                            <div className="document-viewer-container">
                                <LegalDocumentViewer 
                                    documentType={selectedDocument}
                                    onAccept={handleDocumentAccept}
                                    showAcceptButton={true}
                                />
                            </div>
                        )}

                        {!selectedDocument && (
                            <div className="no-document-selected">
                                <InfoCircleOutlined style={{ fontSize: '48px', color: '#1890ff' }} />
                                <Title level={4}>Документ не выбран</Title>
                                <Text type="secondary">
                                    Выберите документ из списка выше для его просмотра
                                </Text>
                            </div>
                        )}
                    </TabPane>

                    <TabPane 
                        tab={
                            <span>
                                <ExclamationCircleOutlined /> Быстрый доступ
                            </span>
                        } 
                        key="quick"
                    >
                        <div className="quick-access">
                            <Title level={4}>Быстрый доступ к документам</Title>
                            <Paragraph>
                                Нажмите на документ для быстрого просмотра в модальном окне
                            </Paragraph>
                            
                            <div className="quick-access-grid">
                                {documentTypes.map(doc => (
                                    <Card
                                        key={doc.key}
                                        className="quick-access-card"
                                        hoverable
                                        onClick={() => showDocumentModal(doc.key)}
                                    >
                                        <div className="quick-access-icon" style={{ color: doc.color }}>
                                            {doc.icon}
                                        </div>
                                        <Title level={5} className="quick-access-title">
                                            {doc.label}
                                        </Title>
                                        <Text type="secondary">
                                            Нажмите для просмотра
                                        </Text>
                                    </Card>
                                ))}
                            </div>
                        </div>
                    </TabPane>
                </Tabs>
            </Card>

            {/* Модальное окно для быстрого просмотра */}
            <Modal
                title="Просмотр документа"
                visible={isModalVisible}
                onOk={handleModalOk}
                onCancel={handleModalCancel}
                width="90%"
                style={{ top: 20 }}
                footer={[
                    <Button key="close" onClick={handleModalCancel}>
                        Закрыть
                    </Button>
                ]}
            >
                {selectedDocument && (
                    <LegalDocumentViewer 
                        documentType={selectedDocument}
                        onAccept={handleDocumentAccept}
                        showAcceptButton={false}
                    />
                )}
            </Modal>
        </div>
    );
};

export default LegalDocuments;
