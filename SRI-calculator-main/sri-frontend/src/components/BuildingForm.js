import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Button, Form, Container } from "semantic-ui-react";
import { BsBuildingFill, BsBuildingFillAdd } from 'react-icons/bs';
import { FaInfo, FaUser } from "react-icons/fa";

import './styling/Mybuilding_new.css'; // Import the CSS file

const BuildingForm = () => {
    const [userInfo, setUserInfo] = useState({});
    const [showUserInfo, setShowUserInfo] = useState(false);
    const [formData, setFormData] = useState({
        building_name: "",
        building_type: "",
        building_usage: "",
        building_state: "",
        energy_class: "",
        zone: "",
        country: "",
        city: "",
        region: "",
        street: "",
        zip: "",
        year_built: "",
    });

    const navigate = useNavigate();
    const [countries, setCountries] = useState([]);

    useEffect(() => {
        const fetchUserInfo = async () => {
            try {
                const token = localStorage.getItem("token");
                const response = await axios.get(`${process.env.REACT_APP_API_URL}/profile`, {
                // const response = await axios.get("http://localhost:8000/profile", {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                setUserInfo(response.data);
            } catch (error) {
                console.error("Error fetching user info", error);
            }
        };
        // const fetchEuropeanCountries = async () => {
        //     try {
        //       const response = await axios.get("https://restcountries.com/v3.1/region/europe");
        //       const countryNames = response.data.map(country => country.name.common);
        //       setCountries(countryNames);
        //     } catch (error) {
        //       console.error("Error fetching countries", error);
        //     }
        //   };
        // fetchEuropeanCountries();
        // fetchUserInfo();
        const EU_COUNTRIES = [
            "Austria",
            "Belgium",
            "Bulgaria",
            "Croatia",
            "Cyprus",
            "Czech Republic",
            "Denmark",
            "Estonia",
            "Finland",
            "France",
            "Germany",
            "Greece",
            "Hungary",
            "Ireland",
            "Italy",
            "Latvia",
            "Lithuania",
            "Luxembourg",
            "Malta",
            "Netherlands",
            "Poland",
            "Portugal",
            "Romania",
            "Slovakia",
            "Slovenia",
            "Spain",
            "Sweden",
          ];  
          const fetchEuropeanUnionCountries = async () => {
            try {
              const response = await axios.get("https://restcountries.com/v3.1/region/europe");
          
              // Filter only countries that are in the EU_COUNTRIES list
              const euCountries = response.data
                .filter(country => EU_COUNTRIES.includes(country.name.common))
                .map(country => country.name.common);
          
              setCountries(euCountries);
            } catch (error) {
              console.error("Error fetching countries", error);
            }
          };
          
          fetchEuropeanUnionCountries();
          fetchUserInfo();  
    }, []);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('token');
            const response = await axios.post(`${process.env.REACT_APP_API_URL}/add_building/`, formData, {
            //const response = await axios.post("http://localhost:8000/add_building/", formData, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            localStorage.setItem('currentBuilding', JSON.stringify(response.data));
            navigate("/present_domains");
        } catch (error) {
            console.error("Error submitting form", error);
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

                {/* Right Section: Form */}
                <div className="profile-welcome">
                    <h1 className="profile-welcome-title">Add a new Building</h1>
                    {/* <div className="building-divider"></div> */}
                    <p className="profile-welcome-text" style={{ fontSize: '24px' }}>To begin a new SRI assessment please provide your building's information:</p>
                    <Container className="building-form-container">
                        <Form className="building-form" onSubmit={handleSubmit}>
                            <Form.Field>
                                <label>Building Name</label>
                                <input
                                    type="text"
                                    name="building_name"
                                    value={formData.building_name}
                                    onChange={handleChange}
                                />
                            </Form.Field>
                            <Form.Field>
                                <label>Building Type</label>
                                <select name="building_type" value={formData.building_type} onChange={handleChange}>
                                    <option value="">Select Building Type</option>
                                    <option value="Residential">Residential</option>
                                    <option value="Non-Residential">Non-Residential</option>
                                </select>
                            </Form.Field>
                            <Form.Field>
                                <label>Building Usage</label>
                                <select name="building_usage" value={formData.building_usage} onChange={handleChange}>
                                    <option value="">Select Building Usage</option>
                                    <option value="Residential - Single Family house">Residential - Single family house</option>
                                    <option value="Residential - Small multi family house">Residential - Small multi family house</option>
                                    <option value="Residential - Large multi family house">Residential - Large multi family house</option>
                                    <option value="Residential - Other">Residential - Other</option>
                                    <option value="Non-Residential - Office">Non-Residential - Office</option>
                                    <option value="Non-Residential - Educational">Non-Residential - Educational</option>
                                    <option value="Non-Residential - Healthcare">Non-Residential - Healthcare</option>
                                    <option value="Non-Residential - Other">Non-Residential - Other</option>
                                </select>
                            </Form.Field>
                            <Form.Field>
                                <label>Building State</label>
                                <select name="building_state" value={formData.building_state} onChange={handleChange}>
                                    <option value="">Select Building Type</option>
                                    <option value="Original">Original</option>
                                    <option value="Renovated">Renovated</option>
                                </select>  
                            </Form.Field>
                            <Form.Field>
                                <label>Energy Class</label>
                                <select name="energy_class" value={formData.energy_class} onChange={handleChange}>
                                    <option value="">Select Class</option>
                                    <option value="Class A">Class A</option>
                                    <option value="Class B">Class B</option>
                                    <option value="Class C">Class C</option>
                                    <option value="Class D">Class D</option>
                                    <option value="Class E">Class E</option>
                                    <option value="Class F">Class F</option>
                                    <option value="Class G">Class G</option>
                                </select>
                            </Form.Field>
                            <Form.Field>
                                <label>Zone</label>
                                <select name="zone" value={formData.zone} onChange={handleChange}>
                                    <option value="">Select Zone</option>
                                    <option value="North Europe">North Europe</option>
                                    <option value="South Europe">South Europe</option>
                                    <option value="West Europe">West Europe</option>
                                    <option value="South-East Europe">South-East Europe</option>
                                    <option value="North-East Europe">North-East Europe</option>
                                </select>
                            </Form.Field>
                            <Form.Field>
                                <label>Country</label>
                                <select name="country" value={formData.country} onChange={handleChange}>
                                    <option value="">Select Country</option>
                                        {countries.map((country, index) => (
                                        <option key={index} value={country}>
                                            {country}
                                        </option>
                                    ))}
                                </select>
                            </Form.Field>
                            <Form.Field>
                                <label>City</label>
                                <input type="text" name="city" value={formData.city} onChange={handleChange} />
                            </Form.Field>
                            <Form.Field>
                            <label>State/Province/Region</label>
                                <input type="text" name="region" value={formData.region} onChange={handleChange} />
                            </Form.Field>
                            <Form.Field>
                                <label>Street and Number</label>
                                <input type="text" name="street" value={formData.street} onChange={handleChange} />
                            </Form.Field>
                            <Form.Field>
                                <label>Zip Code</label>
                                <input type="text" name="zip" value={formData.zip} onChange={handleChange} />
                            </Form.Field>
                            <Form.Field>
                                <label>Building Year</label>
                                <select  name="year_built" value={formData.year_built} onChange={handleChange}>
                                    <option value="">Select Year</option>
                                    <option value="< 1960">{'<'} 1960</option>
                                    <option value="1960 - 1990">1960 - 1990</option>
                                    <option value="1990 - 2010">1990 - 2010</option>
                                    <option value="> 2010">{'>'} 2010</option>
                                    <option value="Not yet constructed">Not yet constructed</option>
                                </select>
                            </Form.Field>
                            <div className="view-sri-button-container">
                                <Button className="view-sri-button" type="submit" primary>Submit</Button>
                            </div>    
                        </Form>
                    </Container>
                </div>
            </div>
        </div>
    );
};

export default BuildingForm;