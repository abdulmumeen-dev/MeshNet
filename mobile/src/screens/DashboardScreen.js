import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  FlatList,
  Animated,
} from 'react-native';
import { Card } from 'react-native-elements';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { LineChart } from 'react-native-chart-kit';
import { Dimensions } from 'react-native';

const screenWidth = Dimensions.get('window').width;

const DashboardScreen = ({ navigation, route }) => {
  const [stats, setStats] = useState({
    nodes: 0,
    gateways: 0,
    bandwidth: 0,
    health: 100,
    speed: 1,
  });
  const [nodes, setNodes] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [trafficData, setTrafficData] = useState({
    labels: ['1m', '2m', '3m', '4m', '5m', '6m', '7m', '8m', '9m', '10m'],
    datasets: [{ data: [20, 45, 28, 80, 99, 43, 50, 75, 60, 85] }],
  });
  const [loading, setLoading] = useState(false);
  const fadeAnim = useState(new Animated.Value(0))[0];

  useEffect(() => {
    fetchStats();
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 1000,
      useNativeDriver: true,
    }).start();
  }, []);

  const fetchStats = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setStats({
        nodes: 12,
        gateways: 4,
        bandwidth: 156.7,
        health: 98,
        speed: 2.4,
      });
      
      setNodes([
        { id: 'n1', ip: '10.0.0.1', status: 'online', role: 'gateway', reputation: 0.95 },
        { id: 'n2', ip: '10.0.0.2', status: 'online', role: 'client', reputation: 0.78 },
        { id: 'n3', ip: '10.0.0.3', status: 'online', role: 'client', reputation: 0.82 },
        { id: 'n4', ip: '10.0.0.4', status: 'offline', role: 'client', reputation: 0.45 },
        { id: 'n5', ip: '10.0.0.5', status: 'online', role: 'gateway', reputation: 0.91 },
      ]);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchStats();
  };

  const renderNode = ({ item }) => (
    <TouchableOpacity
      style={styles.nodeCard}
      onPress={() => navigation.navigate('NodeDetail', { node: item })}
    >
      <View style={styles.nodeLeft}>
        <View style={[styles.nodeDot, { backgroundColor: item.status === 'online' ? '#00d4ff' : '#ff4444' }]} />
        <View>
          <Text style={styles.nodeId}>{item.id}</Text>
          <Text style={styles.nodeIP}>{item.ip}</Text>
        </View>
      </View>
      <View style={styles.nodeRight}>
        {item.role === 'gateway' && (
          <View style={styles.gatewayBadge}>
            <Icon name="router-wireless" size={16} color="#7b2ffc" />
          </View>
        )}
        <Text style={styles.nodeReputation}>{item.reputation.toFixed(2)}</Text>
      </View>
    </TouchableOpacity>
  );

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <Animated.View style={{ opacity: fadeAnim }}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>🌐 MeshNet Ultra</Text>
          <Text style={styles.subtitle}>Network Dashboard</Text>
        </View>

        {/* Stats Grid */}
        <View style={styles.statsGrid}>
          <Card containerStyle={styles.statCard}>
            <Icon name="wifi" size={24} color="#7b2ffc" />
            <Text style={styles.statValue}>{stats.nodes}</Text>
            <Text style={styles.statLabel}>Nodes</Text>
          </Card>
          
          <Card containerStyle={styles.statCard}>
            <Icon name="router-network" size={24} color="#00d4ff" />
            <Text style={styles.statValue}>{stats.gateways}</Text>
            <Text style={styles.statLabel}>Gateways</Text>
          </Card>
          
          <Card containerStyle={styles.statCard}>
            <Icon name="speedometer" size={24} color="#f9a825" />
            <Text style={styles.statValue}>{stats.bandwidth.toFixed(1)}</Text>
            <Text style={styles.statLabel}>Mbps</Text>
          </Card>
          
          <Card containerStyle={styles.statCard}>
            <Icon name="heart-pulse" size={24} color="#00e676" />
            <Text style={styles.statValue}>{stats.health}%</Text>
            <Text style={styles.statLabel}>Health</Text>
          </Card>
        </View>

        {/* Traffic Chart */}
        <Card containerStyle={styles.chartCard}>
          <View style={styles.chartHeader}>
            <Text style={styles.chartTitle}>📊 Network Traffic</Text>
            <TouchableOpacity>
              <Text style={styles.chartMore}>More →</Text>
            </TouchableOpacity>
          </View>
          <LineChart
            data={trafficData}
            width={screenWidth - 40}
            height={200}
            chartConfig={{
              backgroundColor: '#14141e',
              backgroundGradientFrom: '#14141e',
              backgroundGradientTo: '#14141e',
              decimalPlaces: 0,
              color: (opacity = 1) => `rgba(123, 47, 252, ${opacity})`,
              labelColor: (opacity = 1) => `rgba(136, 136, 170, ${opacity})`,
              style: {
                borderRadius: 16,
              },
              propsForDots: {
                r: '6',
                strokeWidth: '2',
                stroke: '#7b2ffc',
              },
            }}
            bezier
            style={styles.chart}
          />
        </Card>

        {/* Quick Actions */}
        <View style={styles.quickActions}>
          <Text style={styles.sectionTitle}>🚀 Quick Actions</Text>
          <View style={styles.actionGrid}>
            <TouchableOpacity style={styles.actionBtn} onPress={() => navigation.navigate('Discovery')}>
              <Icon name="magnify" size={28} color="#7b2ffc" />
              <Text style={styles.actionLabel}>Discover</Text>
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.actionBtn} onPress={() => navigation.navigate('Gateway')}>
              <Icon name="broadcast" size={28} color="#00d4ff" />
              <Text style={styles.actionLabel}>Gateway</Text>
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.actionBtn} onPress={() => navigation.navigate('Connect')}>
              <Icon name="link" size={28} color="#f9a825" />
              <Text style={styles.actionLabel}>Connect</Text>
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.actionBtn} onPress={() => navigation.navigate('Settings')}>
              <Icon name="cog" size={28} color="#aaaacc" />
              <Text style={styles.actionLabel}>Settings</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Nodes List */}
        <View style={styles.nodesSection}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>🔗 Active Nodes</Text>
            <Text style={styles.nodeCount}>{nodes.length} nodes</Text>
          </View>
          {nodes.map((node, index) => renderNode({ item: node }))}
        </View>

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>
            MeshNet Ultra v2.0.0 • {new Date().toLocaleTimeString()}
          </Text>
        </View>
      </Animated.View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a12',
  },
  header: {
    padding: 20,
    paddingTop: 40,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#7b2ffc',
  },
  subtitle: {
    fontSize: 16,
    color: '#666688',
    marginTop: 4,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 10,
    justifyContent: 'space-between',
  },
  statCard: {
    flex: 1,
    minWidth: '45%',
    margin: 5,
    backgroundColor: '#14141e',
    borderRadius: 12,
    padding: 15,
    alignItems: 'center',
    borderWidth: 0,
  },
  statValue: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#e0e0e0',
    marginTop: 8,
  },
  statLabel: {
    fontSize: 12,
    color: '#666688',
    marginTop: 4,
    textTransform: 'uppercase',
  },
  chartCard: {
    margin: 10,
    backgroundColor: '#14141e',
    borderRadius: 12,
    padding: 15,
    borderWidth: 0,
  },
  chartHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  chartTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#aaaacc',
  },
  chartMore: {
    color: '#7b2ffc',
    fontSize: 14,
  },
  chart: {
    borderRadius: 8,
  },
  quickActions: {
    padding: 15,
  },
  actionGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 10,
  },
  actionBtn: {
    backgroundColor: '#14141e',
    padding: 15,
    borderRadius: 12,
    alignItems: 'center',
    flex: 1,
    marginHorizontal: 5,
    borderWidth: 1,
    borderColor: '#2a2a4a',
  },
  actionLabel: {
    color: '#8888aa',
    fontSize: 12,
    marginTop: 6,
  },
  nodesSection: {
    padding: 15,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#aaaacc',
  },
  nodeCount: {
    color: '#666688',
    fontSize: 14,
  },
  nodeCard: {
    backgroundColor: '#14141e',
    padding: 15,
    borderRadius: 10,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#2a2a4a',
  },
  nodeLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  nodeDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 12,
  },
  nodeId: {
    color: '#e0e0e0',
    fontSize: 14,
    fontWeight: '500',
  },
  nodeIP: {
    color: '#666688',
    fontSize: 12,
    marginTop: 2,
  },
  nodeRight: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  gatewayBadge: {
    marginRight: 10,
  },
  nodeReputation: {
    color: '#7b2ffc',
    fontSize: 14,
    fontWeight: 'bold',
  },
  footer: {
    padding: 20,
    alignItems: 'center',
  },
  footerText: {
    color: '#444466',
    fontSize: 12,
  },
});

export default DashboardScreen;
