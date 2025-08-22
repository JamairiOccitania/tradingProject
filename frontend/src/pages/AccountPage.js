import React, { useState, useEffect } from 'react';
import { 
  Container, Paper, Title, TextInput, Button, Group, Stack, 
  Divider, PasswordInput, Modal, Text, Alert, Card, Badge,
  NumberInput, Textarea, Code, Select, Switch, ActionIcon, Tooltip
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { IconUser, IconMail, IconLock, IconTrash, IconCheck, IconX, IconFlask, IconClock, IconPlus, IconEdit, IconTestPipe } from '@tabler/icons-react';
import api from '../services/api';

function AccountPage() {
  const [loading, setLoading] = useState(false);
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [userProfile, setUserProfile] = useState(null);
  const [testLoading, setTestLoading] = useState(false);
  const [taskResults, setTaskResults] = useState([]);
  const [brokerCredentials, setBrokerCredentials] = useState([]);
  const [brokerModalOpen, setBrokerModalOpen] = useState(false);
  const [editingBroker, setEditingBroker] = useState(null);
  const [brokerLoading, setBrokerLoading] = useState(false);
  const [testingConnection, setTestingConnection] = useState(null);

  const profileForm = useForm({
    initialValues: {
      username: '',
      email: '',
      first_name: '',
      last_name: '',
    },
    validate: {
      username: (value) => (value.length < 3 ? 'Le nom d\'utilisateur doit contenir au moins 3 caractères' : null),
      email: (value) => (/^\S+@\S+$/.test(value) ? null : 'Email invalide'),
    },
  });

  const passwordForm = useForm({
    initialValues: {
      old_password: '',
      new_password: '',
      confirm_password: '',
    },
    validate: {
      old_password: (value) => (value.length < 1 ? 'Ancien mot de passe requis' : null),
      new_password: (value) => (value.length < 8 ? 'Le nouveau mot de passe doit contenir au moins 8 caractères' : null),
      confirm_password: (value, values) => 
        value !== values.new_password ? 'Les mots de passe ne correspondent pas' : null,
    },
  });

  const testForm = useForm({
    initialValues: {
      task_type: 'test',
      message: 'Test depuis la page de compte!',
      x: 10,
      y: 25
    }
  });

  const brokerForm = useForm({
    initialValues: {
      broker: '',
      api_key: '',
      api_secret: '',
      account_id: '',
      testnet: true,
      demo: true,
    },
    validate: {
      broker: (value) => (value ? null : 'Veuillez sélectionner un broker'),
      api_key: (value) => (value.length < 10 ? 'Clé API trop courte' : null),
      api_secret: (value, values) => {
        if (values.broker === 'binance' && value.length < 10) {
          return 'Secret API Binance requis';
        }
        if (values.broker === 'ig' && value.length < 6) {
          return 'Mot de passe IG requis';
        }
        return null;
      },
      account_id: (value, values) => {
        if (values.broker === 'oanda' && !value) {
          return 'ID de compte Oanda requis';
        }
        if (values.broker === 'ig' && !value) {
          return 'Nom d\'utilisateur IG requis';
        }
        return null;
      },
    },
  });

  useEffect(() => {
    fetchUserProfile();
    fetchBrokerCredentials();
  }, []);

  const fetchUserProfile = async () => {
    try {
      const response = await api.get('/profile/');
      setUserProfile(response.data);
      profileForm.setValues({
        username: response.data.username || '',
        email: response.data.email || '',
        first_name: response.data.first_name || '',
        last_name: response.data.last_name || '',
      });
    } catch (error) {
      notifications.show({
        title: 'Erreur',
        message: 'Impossible de charger le profil utilisateur',
        color: 'red',
        icon: <IconX size={16} />,
      });
    }
  };

  const fetchBrokerCredentials = async () => {
    try {
      const response = await api.get('/broker-credentials/');
      setBrokerCredentials(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des identifiants broker:', error);
    }
  };

  const handleProfileSubmit = async (values) => {
    setLoading(true);
    try {
      const response = await api.put('/profile/', values);
      setUserProfile(response.data);
      notifications.show({
        title: 'Succès',
        message: 'Profil mis à jour avec succès',
        color: 'green',
        icon: <IconCheck size={16} />,
      });
    } catch (error) {
      notifications.show({
        title: 'Erreur',
        message: error.response?.data?.error || 'Erreur lors de la mise à jour du profil',
        color: 'red',
        icon: <IconX size={16} />,
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordSubmit = async (values) => {
    setPasswordLoading(true);
    try {
      await api.post('/change-password/', values);
      passwordForm.reset();
      notifications.show({
        title: 'Succès',
        message: 'Mot de passe modifié avec succès',
        color: 'green',
        icon: <IconCheck size={16} />,
      });
    } catch (error) {
      notifications.show({
        title: 'Erreur',
        message: error.response?.data?.error || 'Erreur lors du changement de mot de passe',
        color: 'red',
        icon: <IconX size={16} />,
      });
    } finally {
      setPasswordLoading(false);
    }
  };

  const handleTestCelery = async (values) => {
    setTestLoading(true);
    try {
      const response = await api.post('/test-celery/', values);
      const newTask = {
        ...response.data,
        timestamp: new Date().toLocaleString(),
        status: 'PENDING'
      };
      setTaskResults(prev => [newTask, ...prev]);
      
      notifications.show({
        title: 'Tâche lancée',
        message: response.data.message,
        color: 'blue',
        icon: <IconFlask size={16} />,
      });

      // Vérifier le statut de la tâche après 2 secondes
      setTimeout(() => checkTaskStatus(response.data.task_id), 2000);
    } catch (error) {
      notifications.show({
        title: 'Erreur',
        message: 'Impossible de lancer la tâche',
        color: 'red',
        icon: <IconX size={16} />,
      });
    } finally {
      setTestLoading(false);
    }
  };

  const checkTaskStatus = async (taskId) => {
    try {
      const response = await api.get(`/task-status/${taskId}/`);
      setTaskResults(prev => 
        prev.map(task => 
          task.task_id === taskId 
            ? { ...task, ...response.data, checked_at: new Date().toLocaleString() }
            : task
        )
      );
    } catch (error) {
      console.error('Erreur lors de la vérification du statut:', error);
    }
  };

  const handleDeleteAccount = async () => {
    try {
      await api.delete('/delete-account/');
      notifications.show({
        title: 'Compte supprimé',
        message: 'Votre compte a été supprimé avec succès',
        color: 'green',
        icon: <IconCheck size={16} />,
      });
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    } catch (error) {
      notifications.show({
        title: 'Erreur',
        message: 'Erreur lors de la suppression du compte',
        color: 'red',
        icon: <IconX size={16} />,
      });
    }
    setDeleteModalOpen(false);
  };

  const handleBrokerSubmit = async (values) => {
    setBrokerLoading(true);
    try {
      if (editingBroker) {
        await api.put(`/broker-credentials/${editingBroker.id}/`, values);
        notifications.show({
          title: 'Succès',
          message: 'Identifiants broker mis à jour',
          color: 'green',
          icon: <IconCheck size={16} />,
        });
      } else {
        await api.post('/broker-credentials/', values);
        notifications.show({
          title: 'Succès',
          message: 'Identifiants broker ajoutés',
          color: 'green',
          icon: <IconCheck size={16} />,
        });
      }
      
      setBrokerModalOpen(false);
      setEditingBroker(null);
      brokerForm.reset();
      fetchBrokerCredentials();
    } catch (error) {
      notifications.show({
        title: 'Erreur',
        message: error.response?.data?.error || 'Erreur lors de la sauvegarde',
        color: 'red',
        icon: <IconX size={16} />,
      });
    } finally {
      setBrokerLoading(false);
    }
  };

  const handleTestConnection = async (credentialId) => {
    setTestingConnection(credentialId);
    try {
      const response = await api.post(`/broker-credentials/${credentialId}/test/`);
      
      if (response.data.success) {
        notifications.show({
          title: 'Connexion réussie',
          message: response.data.message,
          color: 'green',
          icon: <IconCheck size={16} />,
        });
      } else {
        notifications.show({
          title: 'Échec de la connexion',
          message: response.data.message,
          color: 'red',
          icon: <IconX size={16} />,
        });
      }
    } catch (error) {
      notifications.show({
        title: 'Erreur',
        message: 'Impossible de tester la connexion',
        color: 'red',
        icon: <IconX size={16} />,
      });
    } finally {
      setTestingConnection(null);
    }
  };

  const handleDeleteBroker = async (credentialId) => {
    try {
      await api.delete(`/broker-credentials/${credentialId}/`);
      notifications.show({
        title: 'Succès',
        message: 'Identifiants supprimés',
        color: 'green',
        icon: <IconCheck size={16} />,
      });
      fetchBrokerCredentials();
    } catch (error) {
      notifications.show({
        title: 'Erreur',
        message: error.response?.data?.error || 'Erreur lors de la suppression',
        color: 'red',
        icon: <IconX size={16} />,
      });
    }
  };

  const openBrokerModal = (broker = null) => {
    if (broker) {
      setEditingBroker(broker);
      brokerForm.setValues({
        broker: broker.broker,
        api_key: broker.api_key_decrypted || '',
        api_secret: broker.api_secret_decrypted || '',
        account_id: broker.account_id || '',
        testnet: broker.testnet || false,
        demo: broker.demo || false,
      });
    } else {
      setEditingBroker(null);
      brokerForm.reset();
    }
    setBrokerModalOpen(true);
  };

  if (!userProfile) {
    return <Container>Chargement...</Container>;
  }

  return (
    <Container size="md" py="xl">
      <Title order={1} mb="xl">Gestion de mon compte</Title>

      {/* Informations du profil */}
      <Paper withBorder shadow="md" p="xl" mb="xl">
        <Title order={2} mb="md">Informations personnelles</Title>
        <form onSubmit={profileForm.onSubmit(handleProfileSubmit)}>
          <Stack>
            <Group grow>
              <TextInput
                label="Prénom"
                placeholder="Votre prénom"
                leftSection={<IconUser size={16} />}
                {...profileForm.getInputProps('first_name')}
              />
              <TextInput
                label="Nom"
                placeholder="Votre nom"
                leftSection={<IconUser size={16} />}
                {...profileForm.getInputProps('last_name')}
              />
            </Group>

            <TextInput
              label="Nom d'utilisateur"
              placeholder="Votre nom d'utilisateur"
              required
              leftSection={<IconUser size={16} />}
              {...profileForm.getInputProps('username')}
            />

            <TextInput
              label="Email"
              placeholder="votre@email.com"
              required
              leftSection={<IconMail size={16} />}
              {...profileForm.getInputProps('email')}
            />

            <Group justify="flex-end">
              <Button type="submit" loading={loading}>
                Mettre à jour le profil
              </Button>
            </Group>
          </Stack>
        </form>
      </Paper>

      {/* Changement de mot de passe */}
      <Paper withBorder shadow="md" p="xl" mb="xl">
        <Title order={2} mb="md">Changer le mot de passe</Title>
        <form onSubmit={passwordForm.onSubmit(handlePasswordSubmit)}>
          <Stack>
            <PasswordInput
              label="Ancien mot de passe"
              placeholder="Votre ancien mot de passe"
              required
              leftSection={<IconLock size={16} />}
              {...passwordForm.getInputProps('old_password')}
            />

            <PasswordInput
              label="Nouveau mot de passe"
              placeholder="Votre nouveau mot de passe"
              required
              leftSection={<IconLock size={16} />}
              {...passwordForm.getInputProps('new_password')}
            />

            <PasswordInput
              label="Confirmer le nouveau mot de passe"
              placeholder="Confirmez votre nouveau mot de passe"
              required
              leftSection={<IconLock size={16} />}
              {...passwordForm.getInputProps('confirm_password')}
            />

            <Group justify="flex-end">
              <Button type="submit" loading={passwordLoading}>
                Changer le mot de passe
              </Button>
            </Group>
          </Stack>
        </form>
      </Paper>

      {/* Tests Celery */}
      <Paper withBorder shadow="md" p="xl" mb="xl">
        <Title order={2} mb="md">
          <Group>
            <IconFlask size={24} />
            Tests Celery
          </Group>
        </Title>
        <Text size="sm" c="dimmed" mb="md">
          Testez le fonctionnement des tâches en arrière-plan
        </Text>

        <form onSubmit={testForm.onSubmit(handleTestCelery)}>
          <Stack>
            <Group grow>
              <Button 
                type="submit" 
                loading={testLoading}
                onClick={() => testForm.setFieldValue('task_type', 'test')}
              >
                Test Simple
              </Button>
              <Button 
                type="submit" 
                loading={testLoading}
                color="green"
                onClick={() => testForm.setFieldValue('task_type', 'add')}
              >
                Test Addition
              </Button>
            </Group>

            <Group grow>
              <TextInput
                label="Message de test"
                placeholder="Message personnalisé"
                {...testForm.getInputProps('message')}
              />
            </Group>

            <Group grow>
              <NumberInput
                label="Nombre X"
                {...testForm.getInputProps('x')}
              />
              <NumberInput
                label="Nombre Y"
                {...testForm.getInputProps('y')}
              />
            </Group>
          </Stack>
        </form>

        {/* Résultats des tests */}
        {taskResults.length > 0 && (
          <div>
            <Divider my="md" />
            <Title order={3} mb="md">Résultats des tests</Title>
            <Stack>
              {taskResults.slice(0, 5).map((task, index) => (
                <Card key={index} withBorder p="sm">
                  <Group justify="space-between" mb="xs">
                    <Text size="sm" fw={500}>{task.task_type}</Text>
                    <Badge 
                      color={
                        task.status === 'SUCCESS' ? 'green' : 
                        task.status === 'FAILURE' ? 'red' : 
                        task.status === 'PENDING' ? 'yellow' : 'blue'
                      }
                    >
                      {task.status}
                    </Badge>
                  </Group>
                  <Text size="xs" c="dimmed" mb="xs">
                    <IconClock size={12} style={{ marginRight: 4 }} />
                    {task.timestamp}
                  </Text>
                  <Code block size="xs">
                    Task ID: {task.task_id}
                    {task.result && `\nRésultat: ${JSON.stringify(task.result)}`}
                  </Code>
                  {task.checked_at && (
                    <Text size="xs" c="dimmed" mt="xs">
                      Vérifié à: {task.checked_at}
                    </Text>
                  )}
                </Card>
              ))}
            </Stack>
          </div>
        )}
      </Paper>

      {/* Identifiants Broker */}
      <Paper withBorder shadow="md" p="xl" mb="xl">
        <Group justify="space-between" mb="md">
          <Title order={2}>Identifiants Broker</Title>
          <Button
            leftSection={<IconPlus size={16} />}
            onClick={() => openBrokerModal()}
          >
            Ajouter un broker
          </Button>
        </Group>
        
        <Text size="sm" c="dimmed" mb="md">
          Configurez vos identifiants pour Binance, Oanda et IG afin de pouvoir trader avec vos bots.
        </Text>

        {brokerCredentials.length === 0 ? (
          <Alert color="blue" mb="md">
            <Text>Aucun identifiant broker configuré. Ajoutez vos identifiants pour commencer à trader.</Text>
          </Alert>
        ) : (
          <Stack>
            {brokerCredentials.map((credential) => (
              <Card key={credential.id} withBorder p="md">
                <Group justify="space-between" align="flex-start">
                  <div>
                    <Group mb="xs">
                      <Badge color={
                        credential.broker === 'binance' ? 'yellow' : 
                        credential.broker === 'oanda' ? 'blue' : 
                        credential.broker === 'ig' ? 'green' : 'gray'
                      } size="lg">
                        {credential.broker.toUpperCase()}
                      </Badge>
                      {credential.broker === 'binance' && (
                        <Badge color={credential.testnet ? 'orange' : 'red'} variant="light">
                          {credential.testnet ? 'Testnet' : 'Production'}
                        </Badge>
                      )}
                      {credential.broker === 'ig' && (
                        <Badge color={credential.demo ? 'orange' : 'red'} variant="light">
                          {credential.demo ? 'Démo' : 'Réel'}
                        </Badge>
                      )}
                      <Badge color={credential.is_active ? 'green' : 'gray'} variant="light">
                        {credential.is_active ? 'Actif' : 'Inactif'}
                      </Badge>
                    </Group>
                    
                    <Text size="sm" c="dimmed">
                      <strong>API Key:</strong> {credential.api_key_masked}
                    </Text>
                    {credential.api_secret_masked && (
                      <Text size="sm" c="dimmed">
                        <strong>API Secret:</strong> {credential.api_secret_masked}
                      </Text>
                    )}
                    {credential.account_id && (
                      <Text size="sm" c="dimmed">
                        <strong>Account ID:</strong> {credential.account_id}
                      </Text>
                    )}
                    <Text size="xs" c="dimmed">
                      Ajouté le {new Date(credential.created_at).toLocaleDateString()}
                    </Text>
                  </div>
                  
                  <Group>
                    <Tooltip label="Tester la connexion">
                      <ActionIcon
                        variant="light"
                        color="blue"
                        loading={testingConnection === credential.id}
                        onClick={() => handleTestConnection(credential.id)}
                      >
                        <IconTestPipe size={16} />
                      </ActionIcon>
                    </Tooltip>
                    
                    <Tooltip label="Modifier">
                      <ActionIcon
                        variant="light"
                        color="orange"
                        onClick={() => openBrokerModal(credential)}
                      >
                        <IconEdit size={16} />
                      </ActionIcon>
                    </Tooltip>
                    
                    <Tooltip label="Supprimer">
                      <ActionIcon
                        variant="light"
                        color="red"
                        onClick={() => handleDeleteBroker(credential.id)}
                      >
                        <IconTrash size={16} />
                      </ActionIcon>
                    </Tooltip>
                  </Group>
                </Group>
              </Card>
            ))}
          </Stack>
        )}
      </Paper>

      {/* Zone dangereuse */}
      <Paper withBorder shadow="md" p="xl" style={{ borderColor: '#fa5252' }}>
        <Title order={2} mb="md" c="red">Zone dangereuse</Title>
        <Text mb="md" c="dimmed">
          La suppression de votre compte est irréversible. Toutes vos données seront perdues.
        </Text>
        <Button
          color="red"
          leftSection={<IconTrash size={16} />}
          onClick={() => setDeleteModalOpen(true)}
        >
          Supprimer mon compte
        </Button>
      </Paper>

      {/* Modal de confirmation de suppression */}
      <Modal
        opened={deleteModalOpen}
        onClose={() => setDeleteModalOpen(false)}
        title="Confirmer la suppression"
        centered
      >
        <Alert color="red" mb="md">
          <Text fw={500}>Attention !</Text>
          <Text size="sm">
            Cette action est irréversible. Tous vos bots, backtests et données seront définitivement supprimés.
          </Text>
        </Alert>
        <Group justify="flex-end">
          <Button variant="default" onClick={() => setDeleteModalOpen(false)}>
            Annuler
          </Button>
          <Button color="red" onClick={handleDeleteAccount}>
            Supprimer définitivement
          </Button>
        </Group>
      </Modal>

      {/* Modal Broker */}
      <Modal
        opened={brokerModalOpen}
        onClose={() => {
          setBrokerModalOpen(false);
          setEditingBroker(null);
          brokerForm.reset();
        }}
        title={editingBroker ? "Modifier les identifiants" : "Ajouter un broker"}
        size="md"
      >
        <form onSubmit={brokerForm.onSubmit(handleBrokerSubmit)}>
          <Stack>
            <Select
              label="Broker"
              placeholder="Sélectionnez un broker"
              data={[
                { value: 'binance', label: 'Binance' },
                { value: 'oanda', label: 'Oanda' },
                { value: 'ig', label: 'IG' },
              ]}
              disabled={!!editingBroker}
              {...brokerForm.getInputProps('broker')}
            />

            <TextInput
              label={brokerForm.values.broker === 'ig' ? 'Clé API' : 'Clé API'}
              placeholder={
                brokerForm.values.broker === 'ig' ? 'Votre clé API IG' : 'Votre clé API'
              }
              required
              {...brokerForm.getInputProps('api_key')}
            />

            {brokerForm.values.broker === 'binance' && (
              <>
                <PasswordInput
                  label="Secret API"
                  placeholder="Votre secret API Binance"
                  required
                  {...brokerForm.getInputProps('api_secret')}
                />
                
                <Switch
                  label="Utiliser le testnet Binance"
                  description="Recommandé pour les tests"
                  {...brokerForm.getInputProps('testnet', { type: 'checkbox' })}
                />
              </>
            )}

            {brokerForm.values.broker === 'oanda' && (
              <TextInput
                label="ID de compte"
                placeholder="Votre ID de compte Oanda"
                required
                {...brokerForm.getInputProps('account_id')}
              />
            )}

            {brokerForm.values.broker === 'ig' && (
              <>
                <TextInput
                  label="Nom d'utilisateur"
                  placeholder="Votre nom d'utilisateur IG"
                  required
                  {...brokerForm.getInputProps('account_id')}
                />
                
                <PasswordInput
                  label="Mot de passe"
                  placeholder="Votre mot de passe IG"
                  required
                  {...brokerForm.getInputProps('api_secret')}
                />
                
                <Switch
                  label="Utiliser le compte démo IG"
                  description="Recommandé pour les tests"
                  {...brokerForm.getInputProps('demo', { type: 'checkbox' })}
                />
              </>
            )}
            
            <Group justify="flex-end">
              <Button
                variant="default"
                onClick={() => {
                  setBrokerModalOpen(false);
                  setEditingBroker(null);
                  brokerForm.reset();
                }}
              >
                Annuler
              </Button>
              <Button type="submit" loading={brokerLoading}>
                {editingBroker ? 'Modifier' : 'Ajouter'}
              </Button>
            </Group>
          </Stack>
        </form>
      </Modal>
    </Container>
  );
}

export default AccountPage;
