import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import { Button, Icon, Loader } from 'semantic-ui-react';
import { useNavigate } from 'react-router-dom';
import './styling/Mybuilding.css'; // Import the CSS file
import './styling/Home.css'; // Import the CSS file

const UpgradeSRI = () => {
    const [currentUser, setCurrentUser] = useState(null);
    const [currentBuilding, setCurrentBuilding] = useState(null);
    const { buildingId } = useParams();
    const [currentSRI, setCurrentSRI] = useState(0);
    const [targetSRI, setTargetSRI] = useState("");
    const [upgrades, setUpgrades] = useState({});
    const [originalLevels, setOriginalLevels] = useState({});
    const [newScore, setNewScore] = useState(0);
    const [errorMessage, setErrorMessage] = useState("");
    const [isLoading, setIsLoading] = useState(false); // New state for loading spinner
    const [individualIncreases, setIndividualIncreases] = useState({}); // New state for individual increases
    const navigate = useNavigate();

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
                setCurrentSRI(response.data.total_sri);
            } catch (error) {
                console.error("Error fetching SRI scores", error);
            }
        };
    
        const fetchBuildingInfo = async () => {
            try {
                // const response = await axios.get(`http://localhost:8000/building/${buildingId}/`);
                const response = await axios.get(`${process.env.REACT_APP_API_URL}/building/${buildingId}/`);
                setCurrentBuilding(response.data);
            } catch (error) {
                console.error("Error fetching building info", error);
            }
        };
    
        fetchUserInfo();
        fetchSriScores();
        fetchBuildingInfo();
    }, [buildingId]);

    const handleUpgradeSubmit = async () => {
        if (parseFloat(targetSRI) <= currentSRI) {
            setErrorMessage("Target SRI must be greater than the current SRI.");
            return;
        }

        setIsLoading(true); // Show the loading spinner

        try {
            // const response = await axios.post(`http://localhost:8000/upgrade_sri/${buildingId}/`, {
            const response = await axios.post(`${process.env.REACT_APP_API_URL}/upgrade_sri/${buildingId}/`, {
                target_sri: parseFloat(targetSRI)
            });
            const { Upgrades, Original_Levels, New_Score, Individual_Increases } = response.data;
            setUpgrades(Upgrades);
            setOriginalLevels(Original_Levels);
            setNewScore(New_Score);
            setIndividualIncreases(Individual_Increases); // Set the individual increases
        } catch (error) {
            console.error("Error calculating SRI upgrade:", error);
            setErrorMessage("Failed to upgrade SRI. Please try again.");
        } finally {
            setIsLoading(false); // Hide the loading spinner
        }
    };

    const renderLevel = (levels) => {
        return Object.entries(levels).map(([level, percent]) => (
            <span key={level}>Level {level} ({percent}%)</span>
        )).reduce((prev, curr) => [prev, " & ", curr]);
    };

    const handleLogout = () => {
        localStorage.removeItem("token");
        navigate("/");
    };

    const renderTable = () => {
        return (
            <table>
                <thead>
                    <tr>
                        <th>Service Code</th>
                        <th>Original Levels</th>
                        <th>Upgraded Levels</th>
                        <th>SRI Increase (%)</th> 
                    </tr>
                </thead>
                <tbody>
                    {Object.entries(originalLevels).map(([serviceCode, levels]) => (
                        <tr key={serviceCode}>
                            <td>{serviceCode}</td>
                            <td>{renderLevel(levels)}</td>
                            <td>
                                {renderLevel(upgrades[serviceCode])}
                            </td>
                            <td>{individualIncreases[serviceCode]}%</td> 
                        </tr>
                    ))}
                </tbody>
            </table>
        );
    };

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
    
            <div className="upgrade-main-content">
                <h1 className="upgrade-title">Upgrade SRI</h1>
                <p className="upgrade-current-sri">Current SRI: {currentSRI}%</p>
    
                <div className="upgrade-user-info-card">
                    {currentUser && currentBuilding ? (
                        <div>
                            <p><strong>User:</strong> {currentUser.username}</p>
                            <p><strong>Building:</strong> {currentBuilding.building_name}</p>
                        </div>
                    ) : (
                        <p>Loading user and building information...</p>
                    )}
                </div>
    
                <div className="upgrade-input-section">
                    <label htmlFor="targetSRI">Target SRI:</label>
                    <input
                        type="number"
                        id="targetSRI"
                        value={targetSRI}
                        onChange={(e) => setTargetSRI(e.target.value)}
                    />
                </div>
                <div className="upgrade-submit-section">
                    <button className="upgrade-submit-button" onClick={handleUpgradeSubmit}>Submit</button>
                    {isLoading && <Loader active inline size="small" className="green-loader" />} {/* Show spinner if loading */}
                </div>
                {errorMessage && <p style={{ color: "red" }}>{errorMessage}</p>}
    
                {Object.keys(upgrades).length > 0 && (
                    <div className="upgrades-section">
                        <p className="upgrades-title2">New SRI Score: {newScore}</p>
                        <h2 className="upgrades-title">Recommended Upgrades</h2>
                        <div className="upgrades-table-container">
                            {renderTable()}
                        </div>
                    </div>
                )}
            </div>
    
            <button className="upgrade-back-button" onClick={() => navigate(`/sri_score/${buildingId}`)}>Back</button>
        </div>
    );
};

export default UpgradeSRI;

