import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button, Container, Grid, Segment, Checkbox, Card} from "semantic-ui-react"; // Ensure Button is imported
import axios from 'axios';
import { BsBuildingFill } from 'react-icons/bs';
import { FaInfo, FaUser } from "react-icons/fa";

import './styling/Mybuilding_new.css'; // Import the CSS file

const domains = ["Heating", "Domestic hot water", "Cooling", "Ventilation", "Lighting", "Dynamic building envelope", "Electricity", "Electric vehicle charging",
    "Monitoring and control"];

    const PresentDomains = () => {
        const [selectedDomains, setSelectedDomains] = useState({});
        const [userInfo, setUserInfo] = useState({});
        const [showUserInfo, setShowUserInfo] = useState(false);
        const navigate = useNavigate();
    
        useEffect(() => {
            const fetchUserInfo = async () => {
                try {
                    const token = localStorage.getItem("token");
                    const response = await axios.get(`${process.env.REACT_APP_API_URL}/profile/`, {
                        headers: {
                            Authorization: `Bearer ${token}`,
                        },
                    });
                    setUserInfo(response.data);
                } catch (error) {
                    console.error("Error fetching user info", error);
                }
            };
            fetchUserInfo();
        }, []);
    
        const handleToggle = (domain) => {
            setSelectedDomains((prevSelectedDomains) => ({
                ...prevSelectedDomains,
                [domain]: !prevSelectedDomains[domain],
            }));
        };
    
        const handleSubmit = async () => {
            const building = JSON.parse(localStorage.getItem("currentBuilding"));
            if (building && building.id) {
                const selectedDomainsArray = Object.keys(selectedDomains).filter(domain => selectedDomains[domain]);
    
                try {
                    // const response = await axios.put(`http://localhost:8000/buildings/${building.id}/domains`, {
                    //     domains: selectedDomainsArray
                    // });
                    const response = await axios.put(`${process.env.REACT_APP_API_URL}/buildings/${building.id}/domains`, {
                        domains: selectedDomainsArray
                    });
                    const updatedBuilding = { ...response.data, id: building.id };
                    localStorage.setItem('currentBuilding', JSON.stringify(updatedBuilding));
                    navigate('/services_applications');
                } catch (error) {
                    console.error('Failed to update building domains', error);
                }
            }
        };
    
        const handleLogout = () => {
            localStorage.removeItem("token");
            navigate("/");
        };
    
        const toggleUserInfo = () => {
            setShowUserInfo(!showUserInfo);
        };
    
        return (
            <div className="profile-container">
                {/* Header */}
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
                            <div className="profile-username"><span>{userInfo.username}</span></div>
                            <button className="profile-user-button" onClick={toggleUserInfo}>
                            <FaUser size={20} />
                            </button>
                            {showUserInfo && (
                                <div className="profile-user-details">
                                    <p>{userInfo.email}</p>
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
                    {/* Left Section: Menu */}
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
                    </div>
    
                    {/* Right Section: Present Domains */}
                    <div className="profile-welcome">
                        <h1 className="profile-welcome-title">Present Domains</h1>
                        <p className="profile-welcome-text" style={{ fontSize: '24px' }}>Please provide the domains that are present in your building:</p>
                        {/* <div className="building-divider"></div> */}
                        <Container textAlign="center">
                            <Card centered>
                                <Card.Content>
                                    <Grid centered columns={1}>
                                        {domains.map((domain) => (
                                            <Grid.Row key={domain}>
                                                <Grid.Column>
                                                    <Segment className="domain-grid">
                                                        <div className="domain-name">{domain}</div>
                                                        <div className="domain-button-container">
                                                            <div className={`ui toggle checkbox ${selectedDomains[domain] ? "checked" : ""}`}>
                                                                <input
                                                                    type="checkbox"
                                                                    checked={!!selectedDomains[domain]}
                                                                    onChange={() => handleToggle(domain)}
                                                                />
                                                                <label></label>
                                                            </div>
                                                        </div>
                                                    </Segment>
                                                </Grid.Column>
                                            </Grid.Row>
                                        ))}
                                        <Grid.Row>
                                            <Grid.Column>
                                                <div className="domain-view-sri-button-container">
                                                    <Button className="domain-view-sri-button" onClick={handleSubmit} primary>
                                                        Submit
                                                    </Button>
                                                </div>    
                                            </Grid.Column>
                                        </Grid.Row>
                                    </Grid>
                                </Card.Content>
                            </Card>
                        </Container>
                    </div>
                </div>
            </div>
        );
    };
    
    export default PresentDomains;