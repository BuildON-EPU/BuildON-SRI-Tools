import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Menu, Button, Checkbox, Form, Dropdown, Input, Message, Icon } from 'semantic-ui-react';
import { BsBuildingFill } from 'react-icons/bs';
import { FaInfo, FaUser } from "react-icons/fa";
import './styling/Mybuilding.css'; // Import the CSS file

// Function to get icon based on domain
const getIconForDomain = (domain) => {
    switch (domain) {
        case 'Cooling':
            return 'snowflake';
        case 'Heating':
            return 'thermometer';
        case 'Electricity':
            return 'bolt';
        case 'Lighting':
            return 'lightbulb';
        case 'Domestic hot water':
            return 'shower';
        case 'Monitoring and control':
            return 'laptop';
        case 'Ventilation':
            return 'paper plane';
        case 'Dynamic building envelope':
            return 'home';
        case 'Electric vehicle charging':
            return 'car';
        default:
            return 'question'; // Default icon
    }
};

// const mandatoryServices = {
//     Heating: ['H-3', 'H-4'],
//     'Domestic hot water': ['DHW-3'],
//     Cooling: ['C-1f', 'C-2a', 'C-3', 'C-4'],
//     Ventilation: ['V-1a', 'V-6'],
//     Lighting: ['L-1a', 'L-2'],
//     'Dynamic building envelope': ['DE-2'],
//     Electricity: ['E-12'],
//     'Monitoring and control': ['MC-3', 'MC-4', 'MC-9', 'MC-13', 'MC-25', 'MC-28', 'MC-29', 'MC-30']
// };

const ServicesApplications = () => {
    const [currentUser, setCurrentUser] = useState(null);
    const [currentBuilding, setCurrentBuilding] = useState(null);
    const [activeDomain, setActiveDomain] = useState('');
    const [services, setServices] = useState([]);
    const [domainSelections, setDomainSelections] = useState({});
    const [servicesByDomain, setServicesByDomain] = useState({});
    const [showUserInfo, setShowUserInfo] = useState(false); // State to control user info popup
    const [warningMessage, setWarningMessage] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        const fetchCurrentUser = async () => {
            const token = localStorage.getItem("token");
            try {
                const response = await axios.get(`${process.env.REACT_APP_API_URL}/profile/`, {
                    headers: { Authorization: `Bearer ${token}` },
                });
                setCurrentUser(response.data);
            } catch (error) {
                console.error("Error fetching current user", error);
            }
        };

        const fetchCurrentBuilding = () => {
            const building = JSON.parse(localStorage.getItem("currentBuilding"));
            if (building) {
                setCurrentBuilding(building);
                setActiveDomain(building.domains[0] || '');
            }
        };

        fetchCurrentUser();
        fetchCurrentBuilding();
    }, []);

    useEffect(() => {
        const fetchServices = async (domain) => {
            try {
                // const response = await axios.get(`http://localhost:8000/services/${domain}`);
                const response = await axios.get(`${process.env.REACT_APP_API_URL}/services/${domain}`);
                const serviceData = response.data;

                const filteredServiceData = serviceData.filter(service => !/User defined smart ready service \(\d+\)/.test(service.service_desc));
                setServices(filteredServiceData);

                setServicesByDomain(prev => ({
                    ...prev,
                    [domain]: filteredServiceData
                }));

                setDomainSelections(prev => {
                    const currentDomainSelections = prev[domain] || {};
                    filteredServiceData.forEach(service => {
                        if (!currentDomainSelections[service.service_desc]) {
                            currentDomainSelections[service.service_desc] = { active: false, levels: [], level: null };
                        }
                    });
                    return {
                        ...prev,
                        [domain]: currentDomainSelections
                    };
                });
            } catch (error) {
                console.error('Failed to fetch services', error);
            }
        };

        if (activeDomain) {
            fetchServices(activeDomain);
        }
    }, [activeDomain]);

    const handleServiceToggle = async (service) => {
        setDomainSelections(prev => {
            const currentDomainSelections = prev[activeDomain] || {};
            const currentServiceSelection = currentDomainSelections[service.service_desc] || { active: false, levels: [], level: null, secondaryLevel: null, percentage: '' };
            const updatedServiceSelection = {
                ...currentServiceSelection,
                active: !currentServiceSelection.active
            };

            if (!currentServiceSelection.levels.length && !currentServiceSelection.active) {
                // axios.get(`http://localhost:8000/levels/${service.code}`)
                axios.get(`${process.env.REACT_APP_API_URL}/levels/${service.code}`)
                    .then(response => {
                        const levelData = response.data.map(level => ({
                            desc: level.level_desc + ": " + level.description,
                            intLevel: level.level
                        }));
                        setDomainSelections(prev => {
                            const updatedSelections = { ...prev };
                            updatedSelections[activeDomain][service.service_desc].levels = levelData;
                            return updatedSelections;
                        });
                    })
                    .catch(error => console.error('Failed to fetch levels', error));
            }

            return {
                ...prev,
                [activeDomain]: {
                    ...currentDomainSelections,
                    [service.service_desc]: updatedServiceSelection
                }
            };
        });
    };

    const handleLevelChange = (service, level) => {
        setDomainSelections(prev => {
            const currentDomainSelections = prev[activeDomain] || {};
            return {
                ...prev,
                [activeDomain]: {
                    ...currentDomainSelections,
                    [service.service_desc]: {
                        ...currentDomainSelections[service.service_desc],
                        level,
                        secondaryLevel: null, // Reset secondary level when primary level changes
                        percentage: '' // Reset percentage when primary level changes
                    }
                }
            };
        });
    };

    const handleSecondaryLevelChange = (service, secondaryLevel) => {
        setDomainSelections(prev => {
            const currentDomainSelections = prev[activeDomain] || {};
            return {
                ...prev,
                [activeDomain]: {
                    ...currentDomainSelections,
                    [service.service_desc]: {
                        ...currentDomainSelections[service.service_desc],
                        secondaryLevel,
                        percentage: '' // Reset percentage when secondary level changes
                    }
                }
            };
        });
    };

    const handlePercentageChange = (service, percentage) => {
        // Ensure percentage is not greater than 99
        if (percentage > 99) {
            percentage = 99;
        }
        setDomainSelections(prev => {
            const currentDomainSelections = prev[activeDomain] || {};
            return {
                ...prev,
                [activeDomain]: {
                    ...currentDomainSelections,
                    [service.service_desc]: {
                        ...currentDomainSelections[service.service_desc],
                        percentage
                    }
                }
            };
        });
    };

    const handleSubmit = () => {
        const token = localStorage.getItem("token");

        if (!token) {
            console.error("No token found. Please log in.");
            return;
        }

        // let missingMandatoryServices = false;

        // for (const domain in domainSelections) {
        //     if (mandatoryServices[domain]) {
        //         for (const serviceCode of mandatoryServices[domain]) {
        //             const service = servicesByDomain[domain]?.find(s => s.code === serviceCode);
        //             if (service && (!domainSelections[domain][service.service_desc]?.active || !domainSelections[domain][service.service_desc]?.level)) {
        //                 missingMandatoryServices = true;
        //                 break;
        //             }
        //         }
        //     }
        // }

        // if (missingMandatoryServices) {
        //     setWarningMessage("Please select all the mandatory services before proceeding!");
        //     return;
        // }

        const sriInput = {
            building_type: currentBuilding.building_type,
            zone: currentBuilding.zone,
            dom: currentBuilding.domains,
            lev: {}
        };

        for (const domain in domainSelections) {
            for (const serviceDesc in domainSelections[domain]) {
                const selection = domainSelections[domain][serviceDesc];
                if (selection.active && selection.level) {
                    const service = Object.values(servicesByDomain).flat().find(s => s.service_desc === serviceDesc);
                    if (service) {
                        if (selection.secondaryLevel && selection.percentage) {
                            // If both primary and secondary levels are chosen
                            sriInput.lev[service.code] = {
                                [selection.level.intLevel]: parseInt(selection.percentage, 10),
                                [selection.secondaryLevel.intLevel]: 100 - parseInt(selection.percentage, 10)
                            };
                        } else {
                            // If only the primary level is chosen
                            sriInput.lev[service.code] = {
                                [selection.level.intLevel]: 100
                            };
                        }
                    }
                }
            }
        }

        // axios.post(`http://localhost:8000/calculate-sri/${currentBuilding.id}/`, sriInput, {
        //     headers: { Authorization: `Bearer ${token}` }
        // })
        axios.post(`${process.env.REACT_APP_API_URL}/calculate-sri/${currentBuilding.id}/`, sriInput, {
            headers: { Authorization: `Bearer ${token}` }
        })        
            .then(response => {
                localStorage.setItem('sriData', JSON.stringify(response.data));
                localStorage.setItem('currentUser', JSON.stringify(currentUser));
                localStorage.setItem('currentBuilding', JSON.stringify(currentBuilding));
                navigate(`/sri_score/${currentBuilding.id}`);
            })
            .catch(error => {
                console.error('Failed to calculate SRI', error);
            });
    };

    if (!currentBuilding) {
        return <div>Loading...</div>;
    }

    const handleLogout = () => {
        localStorage.removeItem("token");
        navigate("/");
    };

    const toggleUserInfo = () => {
        setShowUserInfo(!showUserInfo);
    };

    const renderSecondaryFunctionality = (service) => {
        const selection = domainSelections[activeDomain]?.[service.service_desc];
        if (!selection || !selection.level) return null;

        const secondaryOptions = selection.levels
            .filter(level => level.intLevel !== selection.level.intLevel)
            .map(level => ({
                key: level.intLevel,
                value: level,
                text: level.desc
            }));

        secondaryOptions.unshift({
            key: 'none',
            value: null,
            text: 'No Secondary Functionality'
        });

        return (
            <>
                <Form.Field>
                    <label>Secondary Functionality</label>
                    <Dropdown
                        placeholder='Select Secondary Functionality'
                        fluid
                        selection
                        options={secondaryOptions}
                        value={selection.secondaryLevel || null}
                        onChange={(e, { value }) => handleSecondaryLevelChange(service, value)}
                    />
                </Form.Field>
                {selection.secondaryLevel && (
                    <Form.Field>
                        <label>Main Functionality Percentage</label>
                        <Input
                            type='number'
                            placeholder='Enter percentage'
                            min={1}
                            max={99}
                            value={selection.percentage}
                            onChange={(e) => handlePercentageChange(service, e.target.value)}
                        />
                    </Form.Field>
                )}
            </>
        );
    };

    return (
        <div className="profile-container">
            {/* Consistent Header */}
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
                            <div className="profile-username"><span>{currentUser?.username}</span></div>
                            <button className="profile-user-button" onClick={toggleUserInfo}>
                                <FaUser size={20} />
                            </button>
                            {showUserInfo && (
                                <div className="profile-user-details">
                                    <p>{currentUser?.email}</p>
                                    <button className="profile-logout-button" onClick={handleLogout}>Log out</button>
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
    
                <div className="profile-welcome">
                    {/* Left Section: Menu (Profile and Domains) */}
                    <h1 className="profile-welcome-title">Services: Application & Shares</h1>
                    <p className="profile-welcome-text" style={{ fontSize: '24px' }}>Please select the services that are applicable in your building:</p>
                    <div className="content-container"> {/* Add this container */}
                        {/* Domain Selection Menu */}
                        <Menu vertical className="service-menu">
                            {currentBuilding.domains.map(domain => (
                                <Menu.Item
                                    key={domain}
                                    name={domain}
                                    className={`service-menu-item ${activeDomain === domain ? 'active' : ''}`}
                                    onClick={() => setActiveDomain(domain)}
                                >
                                    <Icon name={getIconForDomain(domain)} className="service-menu-icon" />
                                    {domain}
                                </Menu.Item>
                            ))}
                        </Menu>

                        {/* Services & Applications Section */}
                        <div className="services-area">
                            {warningMessage && (
                                <Message
                                    negative
                                    onDismiss={() => setWarningMessage('')}
                                    header="Action Required"
                                    content={warningMessage}
                                />
                            )}
                            <div className="building-content">
                                <div className="services-form">
                                    {services.map(service => (
                                        <div key={service.code} className="service-container">
                                            <div className="service-header">
                                                <span className="service-description" 
                                                //style={{ color: mandatoryServices[activeDomain]?.includes(service.code) ? 'red' : 'black' }}
                                                >
                                                    {service.code + ': ' + service.service_desc}
                                                </span>
                                                <Checkbox
                                                    className="service-checkbox"
                                                    toggle
                                                    checked={domainSelections[activeDomain]?.[service.service_desc]?.active || false}
                                                    onChange={() => handleServiceToggle(service)}
                                                />
                                            </div>
                                            {domainSelections[activeDomain]?.[service.service_desc]?.active && (
                                                <Form className="levels-form">
                                                    {domainSelections[activeDomain]?.[service.service_desc]?.levels.map(level => (
                                                        <Form.Field key={level.intLevel}>
                                                            <Checkbox
                                                                className="level-checkbox"
                                                                radio
                                                                label={level.desc}
                                                                checked={domainSelections[activeDomain]?.[service.service_desc]?.level?.intLevel === level.intLevel}
                                                                onChange={() => handleLevelChange(service, level)}
                                                            />
                                                        </Form.Field>
                                                    ))}
                                                    {renderSecondaryFunctionality(service)}
                                                </Form>
                                            )}
                                        </div>
                                    ))}
                                </div>
                                <Button className="service-view-sri-button" primary onClick={handleSubmit}>Proceed</Button>
                            </div>
                        </div>
                    </div> {/* Close the container */}
                </div>
            </div>
        </div>
    );
};

export default ServicesApplications;

