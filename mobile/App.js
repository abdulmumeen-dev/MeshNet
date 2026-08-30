import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  ScrollView,
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  FlatList,
  Switch,
  ActivityIndicator,
  Alert,
  RefreshControl,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import RNFS from 'react-native-fs';
import { io } from 'socket.io-client';

// Main App Component
const App = () => {
  const [nodes, setNodes] = useState([]);
  const [gateways, setGateways] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isGateway, setIsGateway] = useState(false);
  const [stats, setStats] = useState({
    totalNodes: 0,
    activeGateways: 0,
    totalBandwidth: 0,
    networkHealth: 100,
    speedBoost: 1.0,
  });
  const [logs, setLogs] = useState([]);
  const [targetIP, setTargetIP] = useState('');
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [socket, setSocket] = useState(null);

  // Initialize connection
  useEffect(() => {
    connectToServer();
    loadSettings();
    return () => {
      if (socket) socket.disconnect();
    };
  }, []);

  const connectToServer = async () => {
    try {
      const serverIP = await AsyncStorage.getItem('serverIP') || '192.168.1.100';
      const newSocket = io(`http://${serverIP}:3000`, {
        timeout: 5000,
        reconnection: true,
        reconnectionAttempts: 5,
      });

      newSocket.on('connect', () => {
        setIsConnected(true);
        addLog('info', 'Connected to MeshNet server');
      });

      newSocket.on('disconnect', () => {
        setIsConnected(false);
        addLog('warning', 'Disconnected from server');
      });

      newSocket.on('state_update', (data) => {
        updateState(data.state);
      });

      newSocket.on('update', (data) => {
        updateState(data.state);
        addLog('info', 'Network state updated');
      });

      setSocket(newSocket);
      addLog('info', 'Connecting to MeshNet server...');
    } catch (error) {
      addLog('error', `Connection failed: ${error.message}`);
    }
  };

  const updateState = (state) => {
    if (state) {
      setNodes(Object.values(state.nodes || {}));
      setGateways(Object.values(state.gateways || {}));
      setStats({
        totalNodes: state.stats?.total_nodes || 0,
        activeGateways: state.stats?.active_gateways || 0,
        totalBandwidth: state.stats?.total_bandwidth || 0,
        networkHealth: state.stats?.network_health || 100,
        speedBoost: state.stats?.speed_boost || 1.0,
      });
    }
  };

  const addLog = (level, message) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs((prev) => [
      { timestamp, level, message },
      ...prev.slice(0, 49),
    ]);
  };

  const loadSettings = async () => {
    try {
      const savedIP = await AsyncStorage.getItem('serverIP');
      if (savedIP) setTargetIP(savedIP);
    } catch (error) {
      console.error('Load settings error:', error);
    }
  };

  const saveSettings = async () => {
    try {
      await AsyncStorage.setItem('serverIP', targetIP);
      Alert.alert('Success', 'Settings saved!');
      connectToServer();
    } catch (error) {
      Alert.alert('Error', 'Failed to save settings');
    }
  };

  const controlAction = async (action, data = {}) => {
    if (!socket) return;

    try {
      const response = await fetch(`http://${targetIP}:3000/api/control`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, ...data }),
      });
      const result = await response.json();
      addLog('info', `Action: ${action} - ${result.status}`);
    } catch (error) {
      addLog('error', `Action failed: ${error.message}`);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await controlAction('status');
    setRefreshing(false);
  };

  const renderNode = ({ item }) => (
    <View style={styles.nodeCard}>
      <View style={styles.nodeInfo}>
        <Text style={styles.nodeId}>{item.node_id?.slice(0, 8) || 'Unknown'}</Text>
        <Text style={styles.nodeIP}>{item.ip || 'Unknown IP'}</Text>
      </View>
      <View style={styles.nodeStatus}>
        <View style={[styles.statusDot, item.online ? styles.online : styles.offline]} />
        <Text style={styles.statusText}>
          {item.online ? 'Online' : 'Offline'}
        </Text>
        {item.is_gateway && (
          <View style={styles.gatewayBadge}>
            <Text style={styles.gatewayText}>🌍</Text>
          </View>
        )}
      </View>
    </View>
  );

  const renderLog = ({ item }) => (
    <View style={styles.logEntry}>
      <Text style={styles.logTime}>{item.timestamp}</Text>
      <Text style={[styles.logLevel, styles[`log${item.level}`]]}>
        {item.level.toUpperCase()}
      </Text>
      <Text style={styles.logMessage}>{item.message}</Text>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>🌐 MeshNet Ultra</Text>
          <Text style={styles.subtitle}>Mobile Control Center</Text>
          <View style={styles.connectionStatus}>
            <View style={[styles.statusDot, isConnected ? styles.online : styles.offline]} />
            <Text style={styles.connectionText}>
              {isConnected ? 'Connected' : 'Disconnected'}
            </Text>
          </View>
        </View>

        {/* Stats */}
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Text style={styles.statLabel}>Nodes</Text>
            <Text style={styles.statValue}>{stats.totalNodes}</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statLabel}>Gateways</Text>
            <Text style={styles.statValue}>{stats.activeGateways}</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statLabel}>Bandwidth</Text>
            <Text style={styles.statValue}>{stats.totalBandwidth.toFixed(1)} Mbps</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statLabel}>Speed Boost</Text>
            <Text style={styles.statValue}>{stats.speedBoost.toFixed(1)}x</Text>
          </View>
        </View>

        {/* Controls */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>🎮 Controls</Text>
          <View style={styles.controlsGrid}>
            <TouchableOpacity
              style={[styles.controlBtn, styles.btnPrimary]}
              onPress={() => controlAction('discover')}
            >
              <Text style={styles.btnText}>🔍 Discover</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.controlBtn, styles.btnSuccess]}
              onPress={() => controlAction('gateway')}
            >
              <Text style={styles.btnText}>🌍 Gateway</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.controlBtn, styles.btnWarning]}
              onPress={() => controlAction('status')}
            >
              <Text style={styles.btnText}>📊 Status</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.controlBtn, styles.btnDanger]}
              onPress={() => {
                Alert.alert(
                  'Reset Network',
                  'Are you sure? This will disconnect all nodes.',
                  [
                    { text: 'Cancel', style: 'cancel' },
                    { text: 'Reset', style: 'destructive', onPress: () => controlAction('reset') },
                  ]
                );
              }}
            >
              <Text style={styles.btnText}>🔄 Reset</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Settings */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>⚙️ Settings</Text>
          <View style={styles.settingsRow}>
            <TextInput
              style={styles.input}
              placeholder="Server IP"
              value={targetIP}
              onChangeText={setTargetIP}
              keyboardType="dot-decimal"
            />
            <TouchableOpacity
              style={[styles.controlBtn, styles.btnPrimary, styles.smallBtn]}
              onPress={saveSettings}
            >
              <Text style={styles.btnText}>Save</Text>
            </TouchableOpacity>
          </View>
          <View style={styles.toggleRow}>
            <Text style={styles.toggleLabel}>Quantum Encryption</Text>
            <Switch
              value={true}
              onValueChange={() => {}}
              trackColor={{ false: '#767577', true: '#7b2ffc' }}
            />
          </View>
          <View style={styles.toggleRow}>
            <Text style={styles.toggleLabel}>AI Optimization</Text>
            <Switch
              value={true}
              onValueChange={() => {}}
              trackColor={{ false: '#767577', true: '#7b2ffc' }}
            />
          </View>
        </View>

        {/* Nodes List */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>🔗 Nodes ({nodes.length})</Text>
          {nodes.length > 0 ? (
            <FlatList
              data={nodes}
              renderItem={renderNode}
              keyExtractor={(item, index) => item.node_id || index.toString()}
              scrollEnabled={false}
            />
          ) : (
            <Text style={styles.emptyText}>No nodes connected</Text>
          )}
        </View>

        {/* Logs */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📝 Logs</Text>
          {logs.length > 0 ? (
            <FlatList
              data={logs}
              renderItem={renderLog}
              keyExtractor={(item, index) => index.toString()}
              scrollEnabled={false}
            />
          ) : (
            <Text style={styles.emptyText}>No logs</Text>
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a12',
  },
  header: {
    padding: 20,
    backgroundColor: '#14141e',
    borderBottomWidth: 1,
    borderBottomColor: '#2a2a4a',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#7b2ffc',
  },
  subtitle: {
    fontSize: 14,
    color: '#666688',
    marginTop: 4,
  },
  connectionStatus: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 10,
  },
  connectionText: {
    color: '#8888aa',
    marginLeft: 8,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 15,
    justifyContent: 'space-between',
  },
  statCard: {
    backgroundColor: '#14141e',
    borderWidth: 1,
    borderColor: '#2a2a4a',
    borderRadius: 12,
    padding: 15,
    width: '48%',
    marginBottom: 10,
  },
  statLabel: {
    color: '#666688',
    fontSize: 12,
    textTransform: 'uppercase',
  },
  statValue: {
    color: '#e0e0e0',
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: 5,
  },
  section: {
    padding: 15,
  },
  sectionTitle: {
    color: '#aaaacc',
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 15,
  },
  controlsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  controlBtn: {
    padding: 12,
    borderRadius: 8,
    minWidth: 80,
    alignItems: 'center',
    flex: 1,
  },
  smallBtn: {
    flex: 0.5,
    marginLeft: 10,
  },
  btnText: {
    color: 'white',
    fontWeight: '600',
  },
  btnPrimary: {
    backgroundColor: '#7b2ffc',
  },
  btnSuccess: {
    backgroundColor: '#00d4ff',
  },
  btnWarning: {
    backgroundColor: '#f9a825',
  },
  btnDanger: {
    backgroundColor: '#ff4444',
  },
  settingsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  input: {
    flex: 1,
    backgroundColor: '#1a1a2e',
    borderWidth: 1,
    borderColor: '#2a2a4a',
    borderRadius: 8,
    padding: 12,
    color: '#e0e0e0',
  },
  toggleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#1a1a2e',
  },
  toggleLabel: {
    color: '#aaaacc',
  },
  nodeCard: {
    backgroundColor: '#14141e',
    borderWidth: 1,
    borderColor: '#2a2a4a',
    borderRadius: 8,
    padding: 15,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  nodeInfo: {
    flex: 1,
  },
  nodeId: {
    color: '#7b2ffc',
    fontFamily: 'monospace',
    fontSize: 14,
  },
  nodeIP: {
    color: '#666688',
    fontSize: 12,
    marginTop: 4,
  },
  nodeStatus: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 6,
  },
  online: {
    backgroundColor: '#00d4ff',
  },
  offline: {
    backgroundColor: '#ff4444',
  },
  statusText: {
    color: '#8888aa',
    fontSize: 12,
  },
  gatewayBadge: {
    marginLeft: 8,
    paddingHorizontal: 6,
    paddingVertical: 2,
    backgroundColor: '#7b2ffc22',
    borderRadius: 4,
  },
  gatewayText: {
    fontSize: 14,
  },
  logEntry: {
    flexDirection: 'row',
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: '#0a0a12',
    alignItems: 'center',
  },
  logTime: {
    color: '#444466',
    fontSize: 11,
    width: 70,
  },
  logLevel: {
    fontSize: 10,
    fontWeight: 'bold',
    width: 50,
  },
  loginfo: {
    color: '#00d4ff',
  },
  logwarning: {
    color: '#f9a825',
  },
  logerror: {
    color: '#ff4444',
  },
  logMessage: {
    color: '#8888aa',
    fontSize: 12,
    flex: 1,
  },
  emptyText: {
    color: '#444466',
    textAlign: 'center',
    padding: 20,
  },
});

export default App;
