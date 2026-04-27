import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button, Form, Container, Message } from 'semantic-ui-react';
import './styling/Login.css';

const Signup = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/signup/`, formData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      localStorage.setItem('token', response.data.access_token);
      navigate('/login');
    } catch (error) {
      if (error.response) {
        setError(error.response.data.detail || 'An error occurred during signup');
      } else {
        setError('Error signing up');
      }
    } finally {
      setLoading(false);
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
            <h1 className="login-title">Sign Up</h1>

            <Form onSubmit={handleSubmit} loading={loading} error={!!error} className="login-form">
              <Form.Field>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  placeholder="Username"
                  className="login-input"
                  required
                />
              </Form.Field>
              <Form.Field>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="Email"
                  className="login-input"
                  required
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
                  required
                />
              </Form.Field>

              {error && (
                <Message
                  error
                  header="Signup Failed"
                  content={error}
                />
              )}

              <div className="cta-buttons">
                <Button 
                  type="submit" 
                  className="modern-btn primary-btn" 
                  disabled={loading}
                >
                  <span>Sign Up</span>
                  <div className="btn-shine"></div>
                </Button>

                <Button 
                  type="button" 
                  className="modern-btn secondary-btn"
                  onClick={() => navigate('/login')}
                >
                  <span>Login</span>
                  <div className="btn-shine"></div>
                </Button>
              </div>
            </Form>
          </div>
        </Container>
      </div>

      <footer className="modern-footer">
        <div className="footer-content">
          <img src={require('./assets/footer.png')} alt="Footer Image" className="footer-image" />
        </div>
      </footer>
    </div>
  );
};

export default Signup;


