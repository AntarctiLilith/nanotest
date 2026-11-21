/*
 * Test script for configuration system
 */

// Function to test configuration loading
async function testConfigLoading() {
    console.log('Testing configuration loading...');
    
    try {
        // Attempt to load the JSON configuration
        const response = await fetch('data/streams.json');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const config = await response.json();
        console.log('Configuration loaded successfully:', config);
        
        // Validate required fields
        if (!config.streams || !Array.isArray(config.streams)) {
            console.error('Invalid streams data');
            return false;
        }
        
        console.log('Streams found:', config.streams.length);
        config.streams.forEach((stream, index) => {
            console.log(`Stream ${index + 1}: ${stream.name} (${stream.id})`);
        });
        
        return true;
    } catch (error) {
        console.error('Configuration loading failed:', error);
        return false;
    }
}

// Run the test
testConfigLoading().then(success => {
    if (success) {
        console.log('Configuration test PASSED');
    } else {
        console.log('Configuration test FAILED');
    }
});
