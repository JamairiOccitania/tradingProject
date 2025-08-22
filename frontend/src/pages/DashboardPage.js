import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  Text,
  Title,
  Stack,
  Group,
  Badge,
  SimpleGrid,
  RingProgress,
  ThemeIcon,
  Progress,
  Alert
} from '@mantine/core';
import {
  IconTrendingUp,
  IconRobot,
  IconCurrencyDollar,
  IconChartLine,
  IconAlertTriangle
} from '@tabler/icons-react';
import api from '../services/api';

function DashboardPage() {
  const [stats, setStats] = useState({
    totalBots: 0,
    runningBots: 0,
    totalBalance: 0,
    todayPnL: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/dashboard/');
      setStats({
        totalBots: response.data.totalBots,
        runningBots: response.data.runningBots,
        totalBalance: response.data.totalBalance,
        todayPnL: response.data.todayPnL
      });
      setLoading(false);
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error);
      // Fallback sur des données simulées en cas d'erreur
      setStats({
        totalBots: 0,
        runningBots: 0,
        totalBalance: 0,
        todayPnL: 0
      });
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, icon, color, subtitle }) => (
    <Card withBorder p="lg" radius="md">
      <Group justify="space-between">
        <div>
          <Text c="dimmed" size="sm" tt="uppercase" fw={700}>
            {title}
          </Text>
          <Text fw={700} size="xl">
            {value}
          </Text>
          {subtitle && (
            <Text c="dimmed" size="sm">
              {subtitle}
            </Text>
          )}
        </div>
        <ThemeIcon color={color} size={38} radius="md">
          {icon}
        </ThemeIcon>
      </Group>
    </Card>
  );

  return (
    <Stack gap="lg">
      <Title order={1}>Tableau de bord</Title>
      <Text c="dimmed">
        Bienvenue sur votre plateforme de trading automatisé
      </Text>

      <SimpleGrid cols={{ base: 1, sm: 2, lg: 4 }} spacing="lg">
        <StatCard
          title="Bots totaux"
          value={stats.totalBots}
          icon={<IconRobot size={18} />}
          color="blue"
          subtitle={`${stats.runningBots} en cours`}
        />
        <StatCard
          title="Balance totale"
          value={`${stats.totalBalance.toLocaleString()} €`}
          icon={<IconCurrencyDollar size={18} />}
          color="green"
        />
        <StatCard
          title="P&L aujourd'hui"
          value={`${stats.todayPnL > 0 ? '+' : ''}${stats.todayPnL} €`}
          icon={<IconTrendingUp size={18} />}
          color={stats.todayPnL >= 0 ? "green" : "red"}
        />
        <StatCard
          title="Performance"
          value="85%"
          icon={<IconChartLine size={18} />}
          color="violet"
          subtitle="Taux de réussite"
        />
      </SimpleGrid>

      <Grid>
        <Grid.Col span={{ base: 12, md: 8 }}>
          <Card withBorder p="lg" radius="md">
            <Title order={3} mb="md">Activité des bots</Title>
            <Stack gap="md">
              <Group justify="space-between">
                <Text>Bot RSI Gold</Text>
                <Badge color="green" variant="light">Actif</Badge>
              </Group>
              <Progress value={75} color="green" />
              
              <Group justify="space-between">
                <Text>Bot MACD EUR/USD</Text>
                <Badge color="green" variant="light">Actif</Badge>
              </Group>
              <Progress value={60} color="green" />
              
              <Group justify="space-between">
                <Text>Bot EMA Cross</Text>
                <Badge color="gray" variant="light">Arrêté</Badge>
              </Group>
              <Progress value={0} color="gray" />
            </Stack>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 4 }}>
          <Card withBorder p="lg" radius="md">
            <Title order={3} mb="md">Performance globale</Title>
            <Stack align="center" gap="md">
              <RingProgress
                size={120}
                thickness={12}
                sections={[
                  { value: 85, color: 'green' },
                  { value: 15, color: 'red' }
                ]}
                label={
                  <Text ta="center" fw={700} size="xl">
                    85%
                  </Text>
                }
              />
              <Text ta="center" c="dimmed" size="sm">
                Trades gagnants ce mois
              </Text>
            </Stack>
          </Card>
        </Grid.Col>
      </Grid>

      <Alert
        icon={<IconAlertTriangle size={16} />}
        title="Information"
        color="blue"
        variant="light"
      >
        Vos bots fonctionnent correctement. N'oubliez pas de vérifier régulièrement 
        vos paramètres de risque et vos clés API.
      </Alert>
    </Stack>
  );
}

export default DashboardPage;
