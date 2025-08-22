import React, { useState, useEffect } from 'react';
import { 
  Container, Paper, Title, TextInput, Button, Group, Stack, 
  Divider, PasswordInput, Modal, Text, Alert 
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { IconUser, IconMail, IconLock, IconTrash, IconCheck, IconX } from '@tabler/icons-react';
import api from '../services/api';

function AccountPage() {
  const [loading, setLoading] = useState(false);
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [userProfile, setUserProfile] = useState(null);

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

  useEffect(() => {
    fetchUserProfile();
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
    </Container>
  );
}

export default AccountPage;
