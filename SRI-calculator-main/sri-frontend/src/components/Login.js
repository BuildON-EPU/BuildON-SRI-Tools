import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button, Form, Container } from 'semantic-ui-react';
import './styling/Login.css';

const Login = () => {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/token`, new URLSearchParams({
        username: formData.username,
        password: formData.password
      }));
      localStorage.setItem('token', response.data.access_token);
      navigate('/profile');
    } catch (error) {
      console.error('Error logging in', error);
      alert("Invalid Credentials");
    }
  };

  return (
    <div className="login-page-container">
      <header className="login-header">
        <div className="header-content">
          <div className="logo-section">
            <img src={require('./assets/logo_sri.png')} alt="SRI Logo" className="home-logo" />
          </div>
          <div className="title-section">
            <h1 className="brand-title">SRI Calculator Tool</h1>
            <p className="brand-subtitle">Co-creating Tools and Services for Smart Readiness Indicator</p>
          </div>
        </div>
      </header>

      <div className="login-hero">
        <Container className="login-card-container">
          <div className="login-card">
            <div className="card-glow"></div>
            <h1 className="login-title">Login</h1>

            <Form onSubmit={handleSubmit} className="login-form">
              <Form.Field>
                <input 
                  type="text" 
                  name="username" 
                  value={formData.username} 
                  onChange={handleChange} 
                  placeholder="Username" 
                  className="login-input"
                />
              </Form.Field>
              <Form.Field>
                <input 
                  type="password" 
                  name="password" 
                  value={formData.password} 
                  onChange={handleChange} 
                  placeholder="Password"
                  className="login-input"
                />
              </Form.Field>

              <div className="cta-buttons">
                <Button 
                  type="submit" 
                  className="modern-btn primary-btn"
                >
                  <span>Login</span>
                  <div className="btn-shine"></div>
                </Button>

                <Button 
                  type="button" 
                  className="modern-btn secondary-btn"
                  onClick={() => navigate('/signup')}
                >
                  <span>Sign Up</span>
                  <div className="btn-shine"></div>
                </Button>
              </div>
            </Form>
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

export default Login;
