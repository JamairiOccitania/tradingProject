import React, { useState, useEffect } from 'react';
import {
  Stack,
  Title,
  Card,
  Text,
  Group,
  Badge,
  Button,
  Modal,
  TextInput,
  Select,
  NumberInput,
  Grid,
  ActionIcon,
  Table,
  Loader,
  Center,
  Alert
} from '@mantine/core';
import {
  IconPlus,
  IconPlayerPlay,
  IconPlayerStop,
  IconSettings,
  IconTrash,
  IconRobot,
  IconAlertCircle
} from '@tabler/icons-react';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import api from '../services/api';

function BotsPage() {
  const [bots, setBots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpened, setModalOpened] = useState(false);
  const [editingBot, setEditingBot] = useState(null);

  const form = useForm({
    initialValues: {
      name: '',
      asset: 'XAU_USD',
      strategy: 'RSI_SMA',
      rsi_period: 14,
      sma_period: 50,
      tp: 0.05,
      sl: 0.02,
      position_size: 100,
      mode: 'paper'
    }
  });

  useEffect(() => {
    fetchBots();
  }, []);

  const fetchBots = async () => {
    try {
      const response = await api.get('/bots/');
      setBots(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des bots', error);
      notifications.show({
        title: 'Erreur',
        message: 'Impossible de charger les bots',
        color: 'red',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (values) => {
    try {
      const botData = {
        name: values.name,
        asset: values.asset,
        strategy: values.strategy,
        parameters: {
          rsi_period: values.rsi_period,
          sma_period: values.sma_period,
          tp: values.tp,
          sl: values.sl,
          position_size: values.position_size
        },
        mode: values.mode
      };

      if (editingBot) {
        await api.put(`/bots/${editingBot.id}/`, botData);
        notifications.show({
          title: 'Bot modifié',
          message: 'Le bot a été modifié avec succès',
          color: 'green',
        });
      } else {
        await api.post('/bots/', botData);
        notifications.show({
          title: 'Bot créé',
          message: 'Le bot a été créé avec succès',
          color: 'green',
        });
      }

      fetchBots();
      setModalOpened(false);
      setEditingBot(null);
      form.reset();
    } catch (error) {
      console.error('Erreur lors de la sauvegarde du bot', error);
      notifications.show({
        title: 'Erreur',
        message: 'Impossible de sauvegarder le bot',
        color: 'red',
      });
    }
  };

  const handleStartBot = async (botId) => {
    try {
      await api.post(`/bots/${botId}/start/`);
      notifications.show({
        title: 'Bot démarré',
        message: 'Le bot a été démarré avec succès',
        color: 'green',
      });
      fetchBots();
    } catch (error) {
      notifications.show({
        title: 'Erreur',
        message: 'Impossible de démarrer le bot',
        color: 'red',
      });
    }
  };

  const handleStopBot = async (botId) => {
    try {
      await api.post(`/bots/${botId}/stop/`);
      notifications.show({
        title: 'Bot arrêté',
        message: 'Le bot a été arrêté avec succès',
        color: 'orange',
      });
      fetchBots();
    } catch (error) {
      notifications.show({
        title: 'Erreur',
        message: 'Impossible d\'arrêter le bot',
        color: 'red',
      });
    }
  };

  const handleDeleteBot = async (botId) => {
    try {
      await api.delete(`/bots/${botId}/`);
      notifications.show({
        title: 'Bot supprimé',
        message: 'Le bot a été supprimé avec succès',
        color: 'red',
      });
      fetchBots();
    } catch (error) {
      notifications.show({
        title: 'Erreur',
        message: 'Impossible de supprimer le bot',
        color: 'red',
      });
    }
  };

  const openEditModal = (bot) => {
    setEditingBot(bot);
    form.setValues({
      name: bot.name,
      asset: bot.asset,
      strategy: bot.strategy,
      rsi_period: bot.parameters?.rsi_period || 14,
      sma_period: bot.parameters?.sma_period || 50,
      tp: bot.parameters?.tp || 0.05,
      sl: bot.parameters?.sl || 0.02,
      position_size: bot.parameters?.position_size || 100,
      mode: bot.mode
    });
    setModalOpened(true);
  };

  const openCreateModal = () => {
    setEditingBot(null);
    form.reset();
    setModalOpened(true);
  };

  if (loading) {
    return (
      <Center h={400}>
        <Loader size="lg" />
      </Center>
    );
  }

  return (
    <Stack gap="lg">
      <Group justify="space-between">
        <div>
          <Title order={1}>Mes Bots de Trading</Title>
          <Text c="dimmed">
            Gérez vos bots de trading automatisés
          </Text>
        </div>
        <Button
          leftIcon={<IconPlus size={16} />}
          onClick={openCreateModal}
        >
          Nouveau Bot
        </Button>
      </Group>

      {bots.length === 0 ? (
        <Alert
          icon={<IconRobot size={16} />}
          title="Aucun bot configuré"
          color="blue"
          variant="light"
        >
          Créez votre premier bot de trading pour commencer à automatiser vos stratégies.
        </Alert>
      ) : (
        <Card withBorder>
          <Table>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Nom</Table.Th>
                <Table.Th>Asset</Table.Th>
                <Table.Th>Stratégie</Table.Th>
                <Table.Th>Mode</Table.Th>
                <Table.Th>Statut</Table.Th>
                <Table.Th>Actions</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {bots.map((bot) => (
                <Table.Tr key={bot.id}>
                  <Table.Td>
                    <Text fw={500}>{bot.name}</Text>
                  </Table.Td>
                  <Table.Td>{bot.asset}</Table.Td>
                  <Table.Td>{bot.strategy}</Table.Td>
                  <Table.Td>
                    <Badge
                      color={bot.mode === 'live' ? 'red' : 'blue'}
                      variant="light"
                    >
                      {bot.mode === 'live' ? 'Live' : 'Paper'}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Badge
                      color={bot.status === 'running' ? 'green' : 'gray'}
                      variant="light"
                    >
                      {bot.status === 'running' ? 'Actif' : 'Arrêté'}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Group gap="xs">
                      {bot.status === 'stopped' ? (
                        <ActionIcon
                          color="green"
                          variant="light"
                          onClick={() => handleStartBot(bot.id)}
                        >
                          <IconPlayerPlay size={16} />
                        </ActionIcon>
                      ) : (
                        <ActionIcon
                          color="orange"
                          variant="light"
                          onClick={() => handleStopBot(bot.id)}
                        >
                          <IconPlayerStop size={16} />
                        </ActionIcon>
                      )}
                      <ActionIcon
                        color="blue"
                        variant="light"
                        onClick={() => openEditModal(bot)}
                      >
                        <IconSettings size={16} />
                      </ActionIcon>
                      <ActionIcon
                        color="red"
                        variant="light"
                        onClick={() => handleDeleteBot(bot.id)}
                      >
                        <IconTrash size={16} />
                      </ActionIcon>
                    </Group>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Card>
      )}

      <Modal
        opened={modalOpened}
        onClose={() => {
          setModalOpened(false);
          setEditingBot(null);
          form.reset();
        }}
        title={editingBot ? 'Modifier le Bot' : 'Créer un Nouveau Bot'}
        size="lg"
      >
        <form onSubmit={form.onSubmit(handleSubmit)}>
          <Stack gap="md">
            <TextInput
              label="Nom du bot"
              placeholder="Mon bot de trading"
              required
              {...form.getInputProps('name')}
            />

            <Grid>
              <Grid.Col span={6}>
                <Select
                  label="Asset"
                  data={[
                    { value: 'XAU_USD', label: 'Or (XAU/USD)' },
                    { value: 'EUR_USD', label: 'EUR/USD' },
                    { value: 'GBP_USD', label: 'GBP/USD' },
                    { value: 'USD_JPY', label: 'USD/JPY' }
                  ]}
                  {...form.getInputProps('asset')}
                />
              </Grid.Col>
              <Grid.Col span={6}>
                <Select
                  label="Stratégie"
                  data={[
                    { value: 'RSI_SMA', label: 'RSI + SMA' },
                    { value: 'MACD', label: 'MACD' },
                    { value: 'EMA_CROSS', label: 'EMA Cross' }
                  ]}
                  {...form.getInputProps('strategy')}
                />
              </Grid.Col>
            </Grid>

            <Grid>
              <Grid.Col span={6}>
                <NumberInput
                  label="Période RSI"
                  min={5}
                  max={50}
                  {...form.getInputProps('rsi_period')}
                />
              </Grid.Col>
              <Grid.Col span={6}>
                <NumberInput
                  label="Période SMA"
                  min={10}
                  max={200}
                  {...form.getInputProps('sma_period')}
                />
              </Grid.Col>
            </Grid>

            <Grid>
              <Grid.Col span={4}>
                <NumberInput
                  label="Take Profit"
                  step={0.01}
                  min={0.01}
                  max={1}
                  {...form.getInputProps('tp')}
                />
              </Grid.Col>
              <Grid.Col span={4}>
                <NumberInput
                  label="Stop Loss"
                  step={0.01}
                  min={0.01}
                  max={1}
                  {...form.getInputProps('sl')}
                />
              </Grid.Col>
              <Grid.Col span={4}>
                <NumberInput
                  label="Taille Position"
                  min={1}
                  max={10000}
                  {...form.getInputProps('position_size')}
                />
              </Grid.Col>
            </Grid>

            <Select
              label="Mode de trading"
              data={[
                { value: 'paper', label: 'Paper Trading (Simulation)' },
                { value: 'live', label: 'Live Trading (Réel)' }
              ]}
              {...form.getInputProps('mode')}
            />

            <Group justify="flex-end" mt="md">
              <Button
                variant="light"
                onClick={() => {
                  setModalOpened(false);
                  setEditingBot(null);
                  form.reset();
                }}
              >
                Annuler
              </Button>
              <Button type="submit">
                {editingBot ? 'Modifier' : 'Créer'}
              </Button>
            </Group>
          </Stack>
        </form>
      </Modal>
    </Stack>
  );
}

export default BotsPage;
