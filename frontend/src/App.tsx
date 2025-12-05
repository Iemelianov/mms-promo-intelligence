import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import DiscoveryScreen from './screens/DiscoveryScreen'
import ScenarioLabScreen from './screens/ScenarioLabScreen'
import OptimizationScreen from './screens/OptimizationScreen'
import CreativeScreen from './screens/CreativeScreen'
import PostMortemScreen from './screens/PostMortemScreen'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<DiscoveryScreen />} />
        <Route path="/discovery" element={<DiscoveryScreen />} />
        <Route path="/scenarios" element={<ScenarioLabScreen />} />
        <Route path="/optimization" element={<OptimizationScreen />} />
        <Route path="/creative" element={<CreativeScreen />} />
        <Route path="/postmortem" element={<PostMortemScreen />} />
      </Routes>
    </Layout>
  )
}

export default App
