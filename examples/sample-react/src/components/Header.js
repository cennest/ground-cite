import React, { useState } from 'react';
import { Brain, Settings, Menu, X } from 'lucide-react';
import styles from './styles';
import './Responsive.css';

const Header = ({
    backendStatus,
    onConfigClick,
    error,
    setError
}) => {
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    return (
        <header className="header main-container">
            <div className="header-inner" style={styles.header}>
                <div className="header-glow" style={styles.headerGlow}></div>
                <div className="status-container" style={styles.statusContainer}>

                    <div className="brand-section" style={styles.brandSection}>
                        <div className="logo-brand-container" style={styles.logoBrandContainer}>
                            <img
                                style={styles.logo}
                                src="/logo.png"
                                alt="GroundCite Logo"
                            />
                            <div className="brand-info" style={styles.brandInfo}>
                                <h1 className="title" style={styles.title}>
                                    GroundCite
                                    <span style={styles.titleSub}>for Gemini</span>
                                </h1>
                                <p className="subtitle" style={styles.subtitle}>
                                    Advanced Gemini-powered search with better grounding and citation control
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="status-indicator" style={styles.statusIndicator}>
                        <div className="status-dot" style={{
                            ...styles.statusDot,
                            ...(backendStatus === 'connected' ? styles.statusConnected :
                                backendStatus === 'disconnected' ? styles.statusDisconnected :
                                    styles.statusChecking)
                        }}></div>
                        <span className="status-text" style={{ fontSize: '14px', fontWeight: '600' }}>
                            AI {backendStatus === 'connected' ? 'Online' :
                                backendStatus === 'disconnected' ? 'Offline' : 'Connecting...'}
                        </span>
                    </div>
                </div>
            </div>

            {/* Error Display */}
            {error && (
                <div className="error-alert" style={styles.errorAlert}>
                    <div className="error-alert-inner" style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', flex: 1 }}>
                        <div className="error-icon" style={{
                            color: '#ff4757',
                            fontSize: '18px',
                            minWidth: '20px',
                            marginTop: '2px'
                        }}>
                            âš
                        </div>
                        <div className="error-content" style={{ flex: 1 }}>
                            <h4 className="error-title" style={{
                                color: '#ff6b7a',
                                fontWeight: '600',
                                margin: 0,
                                fontSize: '16px'
                            }}>
                                System Alert
                            </h4>
                            <p className="error-message" style={{
                                color: '#ff8a94',
                                fontSize: '14px',
                                margin: '4px 0 0 0',
                                lineHeight: '1.4'
                            }}>
                                {error}
                            </p>
                        </div>
                    </div>
                    <button
                        className="error-close"
                        onClick={() => setError(null)}
                        style={{
                            background: 'none',
                            border: 'none',
                            color: '#ff4757',
                            cursor: 'pointer',
                            fontSize: '18px',
                            padding: '4px',
                            borderRadius: '4px',
                            minWidth: '28px',
                            height: '28px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}
                    >
                        Ã—
                    </button>
                </div>
            )}

            {/* Configuration Button */}
            <button
                className="config-button"
                onClick={onConfigClick}
                style={styles.configButton}
            >
                <Settings size={14} />
                Configure AI Models
            </button>
        </header>
    );
};

export default Header;