import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Icon } from 'semantic-ui-react';
import { BsBuildingFill, BsBuildingFillAdd } from 'react-icons/bs';
import { FaInfo } from 'react-icons/fa';
import './styling/Profile.css';

const Profile = () => {
    const [user, setUser] = useState(null);
    const [showUserInfo, setShowUserInfo] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchUser = async () => {
            try {
                const token = localStorage.getItem('token');
                if (!token) {
                    navigate('/login');
                    return;
                }

                const response = await axios.get(`${process.env.REACT_APP_API_URL}/profile/`, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });
                setUser(response.data);
            } catch (error) {
                console.error('Error fetching user data:', error);
                alert('Failed to fetch user data. Please login again.');
                navigate('/login');
            }
        };

        fetchUser();
    }, [navigate]);

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/');
    };

    const toggleUserInfo = () => {
        setShowUserInfo(!showUserInfo);
    };

    if (!user) {
        return <div>Loading...</div>;
    }

    return (
        <div className="profile-container">
            {/* Modern Header */}
            <header className="login-header">
                <div className="header-content">
                    <div className="logo-section">
                        <img src={require('./assets/logo_sri.png')} alt="SRI Logo" className="home-logo" />
                    </div>
                    <div className="title-section">
                        <h1 className="brand-title">SRI Calculator Tool</h1>
                        <p className="brand-subtitle">Co-creating Tools and Services for Smart Readiness Indicator</p>
                    </div>
                    <div className="profile-right">
                        <div className="profile-user-info">
                            <div className="profile-username">
                                <span>{user.username}</span>
                            </div>
                            <button className="profile-user-button" onClick={toggleUserInfo}>
                                <Icon name="user" color="white" />
                            </button>
                            {showUserInfo && (
                                <div className="profile-user-details">
                                    <p>{user.email}</p>
                                    <button className="profile-logout-button" onClick={handleLogout}>
                                        Log out
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <div className="profile-main">
                {/* Sidebar Menu */}
                <div className="profile-menu">
                    <div className="profile-button-container">
                        <button className="profile-button my-account" onClick={() => navigate('/profile')}>
                            <FaInfo size={30} />
                            <span className="profile-button-text">About the Tool</span>
                        </button>
                    </div>
                    <div className="profile-button-container">
                        <button className="profile-button my-buildings" onClick={() => navigate('/my_buildings')}>
                            <BsBuildingFill size={30} />
                            <span className="profile-button-text">My Buildings</span>
                        </button>
                    </div>
                    <div className="profile-button-container">
                        <button className="profile-button add-building" onClick={() => navigate('/add_building')}>
                            <BsBuildingFillAdd size={30} />
                            <span className="profile-button-text">Add Building</span>
                        </button>
                    </div>
                </div>

                {/* Welcome Content */}
                <div className="profile-welcome">
                    <h1 className="profile-welcome-title">Welcome to BuildON SRI Calculator Tool!</h1>
                    <p className="profile-welcome-text" style={{ fontSize: '24px' }}>Here you can manage your buildings and review the Smart Readiness Indicator assessments.</p>

                    <div className="profile-card-container">
                        <div className="profile-description-card">
                            <h2>About the tool:</h2>
                            <p>
                                The <strong>Smart Readiness Indicator (SRI) Calculator Tool</strong> is your go-to tool for assessing the smart capabilities of your
                                building. This tool helps you evaluate how well your building can adapt to new technologies, optimize energy
                                efficiency, and enhance the comfort and well-being of its occupants.
                            </p>
                            <p>
                                By providing detailed insights into your building's infrastructure, the SRI Calculator guides you in making informed
                                decisions to improve its smart readiness. Whether you are a building owner, facility manager, or developer, our
                                calculator will help you identify strengths and areas for improvement, ensuring your building is prepared for the future.
                            </p>
                        </div>

                        <div className="profile-description-card">
                            <h2>What is the Smart Readiness Indicator (SRI)?</h2>
                            <p>
                                The <strong>Smart Readiness Indicator (SRI)</strong> is a framework developed by the European Union to measure and assess the smart
                                capabilities of buildings. It evaluates how well a building can incorporate smart technologies to optimize energy use,
                                improve comfort for occupants, and support sustainable living.
                            </p>
                            <p>
                                The SRI considers various factors such as the building's automation systems, energy management, and adaptability to
                                future technological advancements. By understanding your building's SRI, you can identify opportunities to enhance its
                                efficiency, flexibility, and overall performance, making it better equipped to meet the demands of a modern, sustainable
                                environment.
                            </p>
                        </div>

                        <div className="profile-description-card">
                            <h2>About the BuildON Project</h2>
                            <p>
                                <strong>BuildON</strong> is an EU-funded initiative launched in May 2023 under Horizon Europe. It aims to offer affordable and digital solutions to build the next generation of smart and energy-efficient buildings.
                            </p>
                            <p>
                                Over its 42‑month lifespan, the project develops a “Smart Transformer Toolbox”—a suite combining IoT edge/cloud interoperability, AI‑powered MAPO analytics, and Digital Twins—to monitor, benchmark, detect faults, and optimize energy use across five pilot sites in Spain, Finland, Poland, France, and Greece.
                            </p>
                            <p>
                            The Smart Transformer Toolbox includes, among other tools, two dedicated to Smart Readiness Indicator (SRI) assessments: the <strong>SRI Calculator</strong> and <strong>SMURF</strong> (Smart Buildings Readiness Assessment Tool). These tools support building professionals in evaluating current smart readiness and exploring cost-effective upgrade scenarios to enhance performance.
                            </p>
                            <p>
                                BuildON's goal is to transform buildings from static structures into flexible “building‑as‑a‑service” systems, supporting EU climate and digitalization objectives.
                            </p>
                            <p>
                                Learn more at <a href="https://buildon-project.eu/" target="_blank" rel="noopener noreferrer">buildon‑project.eu</a>.
                            </p>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    );
};

export default Profile;


