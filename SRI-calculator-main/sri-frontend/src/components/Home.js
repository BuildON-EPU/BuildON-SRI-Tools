import React from 'react';
import { Button, Container } from 'semantic-ui-react';
import { useNavigate } from 'react-router-dom';
import './styling/Home.css';

const Home = () => {
    const navigate = useNavigate();

    return (
        <div className="home-container">
            <div className="home-header">
                <div className="header-content">
                    <div className="logo-section">
                        <img src={require('./assets/logo_sri.png')} alt="SRI Logo" className="home-logo" />
                    </div>
                    <div className="title-section">
                        <h1 className="brand-title">SRI Calculator Tool</h1>
                        <p className="brand-subtitle">Co-creating Tools and Services for Smart Readiness Indicator</p>
                    </div>
                </div>
            </div>
            
            <div className="hero-section">
                <Container className="hero-content">
                    <div className="welcome-card">
                        <div className="card-glow"></div>
                        <h1 className="hero-title">
                            Welcome to <span className="gradient-text">SRI Toolkit</span>
                        </h1>
                        <p className="hero-description">
                            Empowering smart building assessments with cutting-edge tools
                        </p>
                        <p className="hero-subtitle">Login for Residents and Assessors</p>
                        
                        <div className="cta-buttons">
                            <Button 
                                className="modern-btn primary-btn" 
                                onClick={() => navigate('/login')}
                            >
                                <span>Login</span>
                                <div className="btn-shine"></div>
                            </Button>
                            <Button 
                                className="modern-btn secondary-btn" 
                                onClick={() => navigate('/signup')}
                            >
                                <span>Sign Up</span>
                                <div className="btn-shine"></div>
                            </Button>
                        </div>
                    </div>
                </Container>
            </div>

            <footer className="modern-footer">
                <div className="footer-content">
                    <img src={require('./assets/footer.png')} alt="Footer Partners" className="footer-image" />
                </div>
            </footer>
        </div>
    );
};

export default Home;
