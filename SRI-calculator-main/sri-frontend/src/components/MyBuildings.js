import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Container, Button, Card, Input } from 'semantic-ui-react';
import { useNavigate } from 'react-router-dom';
import { BsBuildingFillAdd } from 'react-icons/bs';
import { FaInfo, FaUser } from 'react-icons/fa';
import DataTable from 'react-data-table-component';
import './styling/Mybuilding_new.css'; // Import the new CSS file
import { Icon } from 'semantic-ui-react'; // Import Icon for user button

// Custom styles for the DataTable component
const customStyles = {
  header: {
    style: {
      fontSize: '18px',
      fontWeight: 'bold',
      backgroundColor: '#5C5DFC', // Theme color for header
      color: 'white',
      textAlign: 'center',
    },
  },
  rows: {
    style: {
      fontSize: '14px',
      padding: '6px',
      justifyContent: 'center', // Center row content
      wordWrap: 'break-word',   // Wrap long words
      whiteSpace: 'normal',     // Allow text to wrap
    },
  },
  headCells: {
    style: {
      backgroundColor: '#5C5DFC', // Theme color for head cells
      color: 'white',
      fontWeight: 'bold',
      fontSize: '16px',
      justifyContent: 'center',  // Center horizontally
      textAlign: 'center',       // Fallback for text alignment
      display: 'flex',           // Use flexbox for centering
      paddingLeft: '40px',
      paddingRight: '0px',
      whiteSpace: 'normal',      // Allow header text to wrap
      wordWrap: 'break-word',    // Wrap long words
    },
  },
  cells: {
    style: {
      justifyContent: 'center', // Flexbox centering
      display: 'flex',           // Ensure centering works
      alignItems: 'center',      // Vertically align
      textAlign: 'center',       // Fallback for text alignment
      whiteSpace: 'normal',      // Allow text to wrap
      wordWrap: 'break-word',    // Wrap long words
    },
  },
  buttonCells: {
    style: {
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
    },
  },
};

const MyBuildings = () => {
  const [buildings, setBuildings] = useState([]);
  const [userInfo, setUserInfo] = useState({});
  const [showUserInfo, setShowUserInfo] = useState(false); // State to control user info popup
  const [searchQuery, setSearchQuery] = useState('');  // State to store search query
  const [message, setMessage] = useState(''); // State for custom message box
  const [showMessageBox, setShowMessageBox] = useState(false); // State to show/hide message box

  const navigate = useNavigate();

  // Function to show custom message box
  const showCustomMessage = (msg) => {
    setMessage(msg);
    setShowMessageBox(true);
  };

  // Function to hide custom message box
  const hideCustomMessage = () => {
    setShowMessageBox(false);
    setMessage('');
  };

  useEffect(() => {
    const fetchBuildings = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/login');
          return;
        }

        const response = await axios.get(`${process.env.REACT_APP_API_URL}/my_buildings/`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setBuildings(response.data);
      } catch (error) {
        console.error('Error fetching buildings:', error);
        showCustomMessage('Failed to fetch buildings. Please try again.');
        // Consider navigating to login after a short delay or user interaction
      }
    };

    const fetchUserInfo = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/login');
          return;
        }

        const response = await axios.get(`${process.env.REACT_APP_API_URL}/profile/`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setUserInfo(response.data);
      } catch (error) {
        console.error('Error fetching user info:', error);
        showCustomMessage('Failed to fetch user information. Please login again.');
        navigate('/login'); // Navigate to login if user info fetch fails
      }
    };

    fetchBuildings();
    fetchUserInfo();
  }, [navigate]);

  const handleViewScores = (buildingId) => {
    navigate(`/sri_score/${buildingId}`);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };

  const toggleUserInfo = () => {
    setShowUserInfo(!showUserInfo);
  };

  // Filter buildings based on the search query
  const filteredBuildings = buildings.filter(building => {
    const lowerCaseQuery = searchQuery.toLowerCase();
    return (
      building.building_name.toLowerCase().includes(lowerCaseQuery) ||
      building.building_type.toLowerCase().includes(lowerCaseQuery) ||
      building.building_usage.toLowerCase().includes(lowerCaseQuery) ||
      building.building_state.toLowerCase().includes(lowerCaseQuery) ||
      building.energy_class.toLowerCase().includes(lowerCaseQuery) ||
      building.zone.toLowerCase().includes(lowerCaseQuery) ||
      building.country.toLowerCase().includes(lowerCaseQuery) ||
      building.city.toLowerCase().includes(lowerCaseQuery) ||
      building.region.toLowerCase().includes(lowerCaseQuery) ||
      building.street.toLowerCase().includes(lowerCaseQuery) ||
      building.zip.toLowerCase().includes(lowerCaseQuery) ||
      (building.year_built && building.year_built.toString().toLowerCase().includes(lowerCaseQuery)) // Ensure year_built is treated as string
    );
  });

  const columns = [
    { name: 'Building Name', selector: row => row.building_name, sortable: true, minWidth: '192px', center: true, className: 'sticky-column'},
    { name: 'Building Type', selector: row => row.building_type, sortable: true, minWidth: '185px', center: true},
    { name: 'Building Usage', selector: row => row.building_usage, sortable: true, minWidth: '200px', center: true},
    { name: 'Building State', selector: row => row.building_state, sortable: true, minWidth: '190px', center: true},
    { name: 'Energy Class', selector: row => row.energy_class, sortable: true, minWidth: '180px', center: true},
    { name: 'Zone', selector: row => row.zone, sortable: true, minWidth: '150px', center: true},
    { name: 'Country', selector: row => row.country, sortable: true, minWidth: '150px', center: true},
    { name: 'City', selector: row => row.city, sortable: true, center: true},
    { name: 'Region', selector: row => row.region, sortable: true, minWidth: '110px', center: true},
    { name: 'Street', selector: row => row.street, sortable: true, center: true},
    { name: 'Zip Code', selector: row => row.zip, sortable: true, minWidth: '145px', center: true},
    { name: 'Building Year', selector: row => row.year_built, sortable: true, minWidth: '180px', center: true},
    {
      name: 'Score',
      cell: row => (
        <div className="view-sri-button-cell"> {/* Added a class for consistent styling */}
          <Button className="view2-sri-button" onClick={() => handleViewScores(row.id)}>
            Expand
          </Button>
        </div>
      ),
    },
  ];

  if (!userInfo.username) {
    return <div>Loading...</div>; // Show loading until user info is fetched
  }

  return (
    <div className="profile-container">
      {/* Custom Message Box */}
      {showMessageBox && (
        <div className="custom-message-box-overlay">
          <div className="custom-message-box">
            <p>{message}</p>
            <button onClick={hideCustomMessage}>OK</button>
          </div>
        </div>
      )}

      {/* Header - This will use styles from profile.css */}
      <header className="login-header"> {/* Use 'login-header' class from profile.css */}
        <div className="header-content"> {/* Use 'header-content' class from profile.css */}
          <div className="logo-section"> {/* Use 'logo-section' class from profile.css */}
            <img src={require('./assets/logo_sri.png')} alt="SRI Logo" className="home-logo" /> {/* Placeholder image */}
          </div>
          <div className="title-section"> {/* Use 'title-section' class from profile.css */}
            <h1 className="brand-title">SRI Calculator Tool</h1> {/* Use 'brand-title' from profile.css */}
            <p className="brand-subtitle">Co-creating Tools and Services for Smart Readiness Indicator</p> {/* Use 'brand-subtitle' from profile.css */}
          </div>
          <div className="profile-right"> {/* Use 'profile-right' from profile.css */}
            <div className="profile-user-info">  
              <div className="profile-username">
                <span>{userInfo.username}</span>
              </div>
              <button className="profile-user-button" onClick={toggleUserInfo}>
                <Icon name="user" /> {/* Using Semantic UI Icon for consistency */}
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

      {/* Main Content - This will use styles from profile.css for overall structure */}
      <div className="profile-main">
        {/* Left Section: Menu - This will use styles from profile.css */}
        <div className="profile-menu">
          <div className="profile-button-container">
            <button className="profile-button my-account" onClick={() => navigate('/profile')}>
              <FaInfo size={30} />
              <span className="profile-button-text">About the Tool</span>
            </button>
          </div>
          <div className="profile-button-container">
            <button className="profile-button my-buildings" onClick={() => navigate('/my_buildings')}>
              <Icon name="building" size="large" /> {/* Semantic UI icon */}
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

        {/* Right Section: My Buildings Table */}
        <div className="profile-welcome">
          <h1 className="profile-welcome-title">My Buildings</h1>
          <p className="profile-welcome-text" style={{ fontSize: '24px' }}>Here is an overview of your buildings:</p>
          <Card centered fluid style={{ padding: '20px', width: '100%', maxWidth: '1200px', backgroundColor: '#ffffff'}}>  {/* Adjusted styles */}
            {/* Search bar and Table in one flex container */}
            <div className="search-table-container" style={{ display: 'column', justifyContent: 'space-between', width: '100%' }}>
              {/* Search bar */}
              <div className="search-bar-container" style={{ display: 'flex', justifyContent: 'flex-end', paddingBottom: '10px', width: '100%', paddingRight: '20px'}}>
                <Input
                  icon="search"
                  placeholder="Search buildings..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  style={{ marginBottom: '10px', width: '300px' }}
                />
              </div>

              {/* Table */}
              <Container>
                <div className="table-container">
                  <DataTable
                    columns={columns}
                    data={filteredBuildings}
                    pagination
                    highlightOnHover
                    responsive
                    fixedHeader
                    fixedHeaderScrollHeight="600px"
                    customStyles={customStyles}
                  />
                </div>
              </Container>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default MyBuildings;

