import React, { useEffect, useState } from 'react';
import { Header, Card, Table, Container, Button, Icon } from 'semantic-ui-react';
import { useParams } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';

import Exporting from 'highcharts/modules/exporting';  // Add this line
import 'highcharts/modules/export-data';               // Optional: Export data module for exporting data as CSV, XLS, etc.


import './styling/Mybuilding.css'; // Import the CSS file
import './styling/Home.css'; // Import the CSS file

// Initialize the Exporting module
Exporting(Highcharts);  // Add this line

const SRIScore = () => {
    const [sriData, setSriData] = useState(null);
    const [currentUser, setCurrentUser] = useState(null);
    const [currentBuilding, setCurrentBuilding] = useState(null);
    const { buildingId } = useParams();
    const navigate = useNavigate();

    useEffect(() => {
        const fetchUserInfo = async () => {
            const token = localStorage.getItem("token");
            try {
              const response = await axios.get("http://localhost:8000/profile/", {
                headers: { Authorization: `Bearer ${token}` },
              });
              setCurrentUser(response.data);
            } catch (error) {
              console.error("Error fetching current user", error);
            }
        };

        const fetchSriScores = async () => {
            try {
                const response = await axios.get(`http://localhost:8000/building/${buildingId}/sri_scores/`);
                setSriData(response.data);
            } catch (error) {
                console.error("Error fetching SRI scores", error);
            }
        };

        const fetchBuildingInfo = async () => {
            try {
                const response = await axios.get(`http://localhost:8000/building/${buildingId}/`);
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

    const domains = [ "Cooling", "Dynamic building envelope", "Domestic hot water", "Electricity", "Electric vehicle charging",
    "Heating", "Lighting", "Monitoring and control", "Ventilation"];

    const getScore = (domain, impactCriterion) => {
        return smart_readiness_scores[`${domain}-${impactCriterion}`] || 0;
    };

    const handleLogout = () => {
        localStorage.removeItem("token");
        navigate("/");
    };

    const handleUpgradeClick = () => {
        navigate(`/upgrade_sri/${buildingId}`);
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
            backgroundColor: {
                linearGradient: [0, 0, 500, 500],
                stops: [
                    [0, 'rgb(255, 255, 255)'],
                    [1, 'rgb(240, 240, 255)']
                ]
            },
            plotBackgroundColor: 'rgba(255, 255, 255, .9)',
            plotShadow: true,
            type: 'column'
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
            min: 0,
            max: 100,
            title: {
                text: 'Score (%)'
            }
        },
        series: [{
            name: 'Domain Scores (%)',
            data: domainScoresData
        }],
        credits: {
            enabled: false // Disable Highcharts.com link
        },
        exporting: {
            enabled: true,   // Enable exporting
            buttons: {
                contextButton: {
                    menuItems: [
                        {
                            text: 'Download PNG',
                            onclick: function () {
                                this.exportChart({ type: 'image/png' });
                            }
                        },
                        {
                            text: 'Download JPEG',
                            onclick: function () {
                                this.exportChart({ type: 'image/jpeg' });
                            }
                        },
                        {
                            text: 'Download PDF',
                            onclick: function () {
                                this.exportChart({ type: 'application/pdf' });
                            }
                        },
                        {
                            text: 'Download SVG',
                            onclick: function () {
                                this.exportChart({ type: 'image/svg+xml' });
                            }
                        }
                    ]
                }
            },
            filename: 'SRI_Score_DomainChart',
            sourceWidth: 800,
            sourceHeight: 600
        }
    };

    // Impact Criteria Scores chart options
    const impactCriteriaOptions = {
        chart: { 
            backgroundColor: {
                linearGradient: [0, 0, 500, 500],
                stops: [
                    [0, 'rgb(255, 255, 255)'],
                    [1, 'rgb(240, 240, 255)']
                ]
            },
            plotBackgroundColor: 'rgba(255, 255, 255, .9)',
            plotShadow: true,
            type: 'column'
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
            min: 0,
            max: 100,
            title: {
                text: 'Score (%)'
            }
        },
        series: [{
            name: 'Impact Scores (%)',
            data: impactCriteriaData
        }],
        credits: {
            enabled: false // Disable Highcharts.com link
        },
        exporting: {
            enabled: true,   // Enable exporting
            buttons: {
                contextButton: {
                    menuItems: ['downloadPNG', 'downloadJPEG', 'downloadPDF', 'downloadSVG']
                }
            },
            filename: 'SRI_Score_ImpactChart',
            sourceWidth: 800,
            sourceHeight: 600
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
        <div className="sri-score-page">
            <div className="header-section">
                <div className="logo-title">
                <img src={require('./assets/logo_sri.png')} alt="SRI Logo" className="logo" />
                    <div>
                        <h1 className="main-title">SRI-TOOLKIT</h1>
                        <h2 className="building-subtitle">Co-creating Tools and Services for Smart Readiness Indicator</h2>
                    </div>
                </div>
                <button className="sri-building-button sri-my-account" title="View Profile" onClick={() => navigate('/profile')}>
                    <Icon name="user" size="huge" />
                </button>
                <button className="sri-building-button sri-my-buildings" title="View your Buildings" onClick={() => navigate('/my_buildings')}>
                    <Icon name="building" size="huge" />
                </button>
                <button className="sri-building-button sri-add-building" title="Add a new Building" onClick={() => navigate('/add_building')}>
                    <Icon name="plus" size="huge" />
                </button>
                <Button icon onClick={handleLogout} title="Log out" className="logout-button">
                    <Icon name='log out' />
                </Button>
            </div>

            <div className="info-cards">
                <Card className="info-card">
                    <Card.Content>
                        <Card.Header style={{ color: 'green' }}>User Information</Card.Header>
                        <Card.Meta style={{ color: 'black' }}>Username: {currentUser.username}</Card.Meta>
                        <Card.Meta style={{ color: 'black' }}>Email: {currentUser.email}</Card.Meta>
                    </Card.Content>
                </Card>
                <div className="total-sri-score">
                    Total SRI Score: {total_sri}% 
                    <div className="building-class">
                        SRI Class: {buildingClass}
                    </div>
                    <Button className='upgrade-sri-button'
                    primary 
                    style={{ marginTop: '20px' }} 
                    onClick={handleUpgradeClick}
                >
                    Upgrade SRI
                </Button>
                </div>
                <Card className="info-card">
                    <Card.Content>
                        <Card.Header style={{ color: 'green' }}>Building Information</Card.Header>
                        <Card.Meta style={{ color: 'black' }}>Building Name: {currentBuilding.building_name}</Card.Meta>
                        <Card.Meta style={{ color: 'black' }}>Building Type: {currentBuilding.building_type}</Card.Meta>
                        <Card.Meta style={{ color: 'black' }}>Zone: {currentBuilding.zone}</Card.Meta>
                        <Card.Meta style={{ color: 'black' }}>Country: {currentBuilding.country}</Card.Meta>
                        <Card.Meta style={{ color: 'black' }}>City: {currentBuilding.city}</Card.Meta>
                        <Card.Meta style={{ color: 'black' }}>Year: {currentBuilding.year_built}</Card.Meta>
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
    );
};

export default SRIScore;