import React, { useState } from 'react';
import { Container, Paper, Title, PasswordInput, Button, Text, Alert, Group, Anchor } from '@mantine/core';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { IconLock, IconCheck, IconX } from '@tabler/icons-react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';

function ResetPasswordPage() {
  const [loading, setLoading] = useState(false);
  const { uid, token } = useParams();
  const navigate = useNavigate();

  const form = useForm({
    initialValues: {
      newPassword: '',
      confirmPassword: '',
    },
    validate: {
      newPassword: (value) => (value.length < 8 ? 'Le mot de passe doit contenir au moins 8 caractères' : null),
      confirmPassword: (value, values) => 
        value !== values.newPassword ? 'Les mots de passe ne correspondent pas' : null,
    },
  });

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      await api.post('/password-reset-confirm/', {
        uid: uid,
        token: token,
        new_password: values.newPassword,
      });
      
      notifications.show({
        title: 'Succès',
        message: 'Votre mot de passe a été réinitialisé avec succès',
        color: 'green',
        icon: <IconCheck size={16} />,
      });
      
      setTimeout(() => navigate('/login'), 2000);
    } catch (error) {
      notifications.show({
        title: 'Erreur',
        message: error.response?.data?.error || 'Le lien de réinitialisation est invalide ou expiré',
        color: 'red',
        icon: <IconX size={16} />,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container size={420} my={40}>
      <Paper withBorder shadow="md" p={30} mt={30} radius="md">
        <Title ta="center" mb="md">
          Nouveau mot de passe
        </Title>
        <Text c="dimmed" size="sm" ta="center" mb="md">
          Entrez votre nouveau mot de passe
        </Text>

        <form onSubmit={form.onSubmit(handleSubmit)}>
          <PasswordInput
            label="Nouveau mot de passe"
            placeholder="Votre nouveau mot de passe"
            required
            leftSection={<IconLock size={16} />}
            {...form.getInputProps('newPassword')}
            mb="md"
          />

          <PasswordInput
            label="Confirmer le mot de passe"
            placeholder="Confirmez votre nouveau mot de passe"
            required
            leftSection={<IconLock size={16} />}
            {...form.getInputProps('confirmPassword')}
          />

          <Button
            type="submit"
            fullWidth
            mt="xl"
            loading={loading}
          >
            Réinitialiser le mot de passe
          </Button>
        </form>

        <Group justify="center" mt="lg">
          <Anchor component={Link} to="/login" size="sm">
            Retour à la connexion
          </Anchor>
        </Group>
      </Paper>
    </Container>
  );
}

export default ResetPasswordPage;
