import React, { useEffect, useState } from 'react';
import { Header, Card, Table, Container, Button, Icon } from 'semantic-ui-react';
import { useParams } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';
import Exporting from 'highcharts/modules/exporting';
import ExportData from 'highcharts/modules/export-data';
import './styling/Mybuilding_new.css'; // Import the CSS file
import './styling/Home.css'; // Import the CSS file
import { BsBuildingFill } from 'react-icons/bs';
import { FaInfo, FaUser } from "react-icons/fa";

// Initialize the modules
Exporting(Highcharts);
ExportData(Highcharts);

const SRIScore = () => {
    const [sriData, setSriData] = useState(null);
    const [currentUser, setCurrentUser] = useState(null);
    const [currentBuilding, setCurrentBuilding] = useState(null);
    const { buildingId } = useParams();
    const navigate = useNavigate();

    const [showUserInfo, setShowUserInfo] = useState(false);


    useEffect(() => {
        const fetchUserInfo = async () => {
            const token = localStorage.getItem("token");
            try {
                // const response = await axios.get("http://localhost:8000/profile/", {
                const response = await axios.get(`${process.env.REACT_APP_API_URL}/profile/`, {
                    headers: { Authorization: `Bearer ${token}` },
                });
                setCurrentUser(response.data);
            } catch (error) {
                console.error("Error fetching current user", error);
            }
        };

        const fetchSriScores = async () => {
            try {
                // const response = await axios.get(`http://localhost:8000/building/${buildingId}/sri_scores/`);
                const response = await axios.get(`${process.env.REACT_APP_API_URL}/building/${buildingId}/sri_scores/`);
                setSriData(response.data);
            } catch (error) {
                console.error("Error fetching SRI scores", error);
            }
        };

        const fetchBuildingInfo = async () => {
            try {
                // const response = await axios.get(`http://localhost:8000/building/${buildingId}/`);
                const response = await axios.get(`${process.env.REACT_APP_API_URL}/building/${buildingId}/`);
                console.log("Fetched Building Info:", response.data);  
                setCurrentBuilding(response.data);
            } catch (error) {
                console.error("Error fetching building info", error);
            }
        };

        fetchUserInfo();
        fetchSriScores();
        fetchBuildingInfo();
    }, [buildingId]);

    console.log(sriData);
    console.log(currentUser);
    console.log(currentBuilding);

    if (!sriData || !currentUser || !currentBuilding) {
        return <h2>Loading...</h2>;
    }

    const { 
        smart_readiness_scores, 
        sr_impact_criteria, 
        sr_domains,
        srf_scores, 
        total_sri 
    } = sriData;

    const impactCriteria = [
        "Energy efficiency", "Energy, flexibility and storage", "Comfort", "Convenience", "Health, wellbeing and accessibility", 
        "Maintenance and fault prediction", "Information to occupants"
    ];

    const domains = [ "Heating", "Domestic hot water", "Cooling", "Ventilation", "Lighting", "Dynamic building envelope", "Electricity", 
        "Electric vehicle charging", "Monitoring and control"];

    const getScore = (domain, impactCriterion) => {
        return smart_readiness_scores[`${domain}-${impactCriterion}`] || 0;
    };

    const handleLogout = () => {
        localStorage.removeItem("token");
        navigate("/");
    };

const handleUpgradeClick = async () => {
    if (!buildingId || !sriData || !currentBuilding) {
        console.error("Missing data: Building Id, SRI data, or Building data.");
        return;
    }

    try {
        // Retrieve the token from localStorage
        const token = localStorage.getItem('token');
        if (!token) {
            console.error("Authorization token is missing.");
            return;
        }

        // Construct the SRIInput object to send to FastAPI
        const sriInput = {
            building_type: currentBuilding.building_type,
            zone: currentBuilding.zone,
            dom: Object.keys(sriData.sr_domains),  // Domains
            lev: Object.entries(currentBuilding.levels).reduce((acc, [service_code, levelObj]) => {
                const level = Object.keys(levelObj)[0];
                const percentage = levelObj[level];
                acc[service_code] = { [level]: percentage };
                return acc;
            }, {})
        };

        console.log("Sending SRIInput to FastAPI:", sriInput);

        // Step 1: Make the POST request to FastAPI to generate the dst_format
        // const upgradeResponse = await axios.post(
        //     `http://localhost:8000/upgrade-scenarios/${buildingId}/`,
        const upgradeResponse = await axios.post(
            `${process.env.REACT_APP_API_URL}/upgrade-scenarios/${buildingId}/`,
            sriInput,
            {
                headers: {
                    Authorization: `Bearer ${token}`,  // Token Authorization
                    'Content-Type': 'application/json',  // Set content-type
                }
            }
        );

        // Check if FastAPI response is successful
        if (upgradeResponse.status !== 200) {
            console.error(`Error from FastAPI: ${upgradeResponse.status} - ${upgradeResponse.statusText}`);
            return;
        }

        // Step 2: Extract the dst_format from the FastAPI response
        const dstFormat = upgradeResponse.data;
        console.log("Response from FastAPI (dst_format):", dstFormat);

        // Instead of sending it to Django immediately, redirect to the Django form page
        // Encode the dstFormat data as part of the session or URL if needed
        //window.location.href = `http://localhost:8001/smurf/set/srigoal/${buildingId}/`;
        window.location.href = `https://sri.buildon.epu.ntua.gr/smurf/set/srigoal/${buildingId}/`;

    } catch (error) {
        console.error("Error during upgrade or DST submission:", error.response?.data || error.message);
    }
};

    // Prepare data for Domain Scores chart
    const domainScoresData = domains.map(domain => ({
        name: domain,
        y: sr_domains[domain] || 0,
    }));

    // Prepare data for Impact Criteria Scores chart
    const impactCriteriaData = Object.entries(sr_impact_criteria).map(([key, value]) => ({
        name: key,
        y: value,
    }));

    // Domain Scores chart options
    const domainScoresOptions = {
        chart: { 
            backgroundColor: '#f5f5f5',
            plotBackgroundColor: 'white',
            // plotShadow: true,
            type: 'column',
            height: 500 // Match this with the container height
        },
        title: {
            text: 'Domain Scores'
        },
        xAxis: {
            categories: domains,
            title: {
                text: 'Domains'
            }
        },
        yAxis: {
            min: null,  // Allows negative values as well
            max: 100,
            title: {
                text: 'Score (%)'
            }
        },
        series: [{
            name: 'Domain Scores (%)',
            data: domainScoresData,
            color: '#5C5DFC'  // Change this to your desired color
        }],
        credits: {
            enabled: false  // This hides the Highcharts credits
        },
        exporting: {
            enabled: true  // Enable the exporting module
        }
    };

    // Impact Criteria Scores chart options
    const impactCriteriaOptions = {
        chart: { 
            backgroundColor: '#f5f5f5',
            plotBackgroundColor: 'white',
            // plotShadow: true,
            type: 'column',
            height: 500 // Match this with the container height
        },
        title: {
            text: 'Impact Criteria Scores'
        },
        xAxis: {
            categories: Object.keys(sr_impact_criteria),
            title: {
                text: 'Impact Criteria'
            }
        },
        yAxis: {
            min: null,  // Allows negative values as well
            max: 100,
            title: {
                text: 'Score (%)'
            }
        },
        series: [{
            name: 'Impact Scores (%)',
            data: impactCriteriaData,
            color: '#5C5DFC'  // Change this to your desired color
        }],
        credits: {
            enabled: false  // This hides the Highcharts credits
        },
        exporting: {
            enabled: true  // Enable the exporting module
        }
    };

    // Function to get building class based on total SRI score
    const getBuildingClass = (score) => {
        if (score >= 90) return "A";
        if (score >= 80) return "B";
        if (score >= 65) return "C";
        if (score >= 50) return "D";
        if (score >= 35) return "E";
        if (score >= 20) return "F";
        return "G";
    };

    const buildingClass = getBuildingClass(total_sri);

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
                            <div className="profile-username"><span>{currentUser?.username}</span></div>
                            <button className="profile-user-button" onClick={handleLogout}>
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

                {/* Right Section: SRI Score Information */}
                <div className="profile-welcome">
                    <div className="info-cards">
                        <Card className="info-card">
                            <Card.Content>
                                <Card.Header style={{ color: '#5C5DFC' }}><b>User Information</b></Card.Header>
                                <Card.Meta style={{ color: '#474744' , fontSize: '18px'}}><b>Username: {currentUser.username}</b></Card.Meta>
                                <Card.Meta style={{ color: '#474744' , fontSize: '18px'}}><b>Email: {currentUser.email}</b></Card.Meta>
                            </Card.Content>
                        </Card>
                        <div className="total-sri-score">
                            Total SRI Score: {total_sri}% 
                            <div className="building-class">
                                SRI Class: {buildingClass}
                            </div>
                            <Button className='service-view-sri-button'
                            primary 
                            style={{ marginTop: '20px' }} 
                            onClick={handleUpgradeClick}
                        >
                            Upgrade
                        </Button>
                        </div>
                        <Card className="info-card">
                            <Card.Content>
                                <Card.Header style={{ color: '#5C5DFC' }}><b>Building Information</b></Card.Header>
                                <Card.Meta style={{ color: '#474744' , fontSize: '18px'}}><b>Building Name: {currentBuilding.building_name}</b></Card.Meta>
                                <Card.Meta style={{ color: '#474744' , fontSize: '18px'}}><b>Building Type: {currentBuilding.building_type}</b></Card.Meta>
                                <Card.Meta style={{ color: '#474744' , fontSize: '18px'}}><b>Climate Zone: {currentBuilding.zone}</b></Card.Meta>
                                <Card.Meta style={{ color: '#474744' , fontSize: '18px'}}><b>Country: {currentBuilding.country}</b></Card.Meta>
                                <Card.Meta style={{ color: '#474744' , fontSize: '18px'}}><b>City: {currentBuilding.city}</b></Card.Meta>
                                <Card.Meta style={{ color: '#474744' , fontSize: '18px'}}><b>Year of Construction: {currentBuilding.year_built}</b></Card.Meta>
                            </Card.Content>
                        </Card>
                    </div>

                    <h3 className="detailed-scores-title">Detailed Scores</h3>
                    <Table celled className="detailed-scores-table">
                        <Table.Header>
                            <Table.Row>
                                <Table.HeaderCell className="bold-text">Domains\Impact Criteria</Table.HeaderCell>
                                {impactCriteria.map(ic => (
                                    <Table.HeaderCell key={ic} className="bold-text">{ic}</Table.HeaderCell>
                                ))}
                            </Table.Row>
                        </Table.Header>
                        <Table.Body>
                            {domains.map(domain => (
                                <Table.Row key={domain}>
                                    <Table.Cell className="bold-text">{domain}</Table.Cell>
                                    {impactCriteria.map(ic => (
                                        <Table.Cell key={`${domain}-${ic}`}>{getScore(domain, ic)}%</Table.Cell>
                                    ))}
                                </Table.Row>
                            ))}
                        </Table.Body>
                    </Table>

                    <h3 className="detailed-scores-title">Domain Scores</h3>
                    <Container className='horizontal-container'>
                        <Container className="scores-charts-container">
                            <div className="scores-table">
                                <h4 textAlign='center'>Domain Scores</h4>
                                <Table celled className="small-table">
                                    <Table.Body>
                                        {domains.map(domain => (
                                            <Table.Row key={domain}>
                                                <Table.Cell className="bold-text">{domain}</Table.Cell>
                                                <Table.Cell>{sr_domains[domain] || 0}%</Table.Cell>
                                            </Table.Row>
                                        ))}
                                    </Table.Body>
                                </Table>
                            </div>
                            <div className='chart-space'>
                                <HighchartsReact highcharts={Highcharts} options={domainScoresOptions} />
                            </div>
                        </Container>
                    </Container> 

                    <h3 className="detailed-scores-title">Impact Criteria Scores</h3>
                    <Container className='horizontal-container'>
                        <Container className="scores-charts-container">
                            <div className="scores-table">
                            <h4 textAlign='center'>Impact Criteria Scores</h4>
                                <Table celled className="small-table">
                                    <Table.Body>
                                        {Object.entries(sr_impact_criteria).map(([key, value]) => (
                                            <Table.Row key={key}>
                                                <Table.Cell className="bold-text">{key}</Table.Cell>
                                                <Table.Cell>{value}%</Table.Cell>
                                            </Table.Row>
                                        ))}
                                    </Table.Body>
                                </Table>
                            </div>
                            <div className='chart-space'>
                                <HighchartsReact highcharts={Highcharts} options={impactCriteriaOptions} />
                            </div>
                        </Container>
                    </Container>

                    <h3 className="detailed-scores-title">Key Functionality Scores</h3>
                    <Container className="srf-scores-container">
                        <Header as='h4' textAlign='center'>Key Functionality Scores</Header>
                        <Table celled className="small-table">
                            <Table.Body>
                                {Object.entries(srf_scores).map(([key, value]) => (
                                    <Table.Row key={key}>
                                        <Table.Cell className="bold-text">{key}</Table.Cell>
                                        <Table.Cell>{value}%</Table.Cell>
                                    </Table.Row>
                                ))}
                            </Table.Body>
                        </Table>
                    </Container>
                </div>
            </div>
        </div>
    );
};

export default SRIScore;

