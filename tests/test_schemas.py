"""Tests for schema models."""


from sxth_mind.schemas import ConversationMemory, ProjectMind, UserMind


class TestUserMind:
    def test_create_with_defaults(self):
        user_mind = UserMind(user_id="test_user")

        assert user_mind.user_id == "test_user"
        assert user_mind.trust_score == 0.5
        assert user_mind.total_interactions == 0
        assert user_mind.preferred_tone == "balanced"
        assert user_mind.identity_data == {}
        assert user_mind.patterns == {}

    def test_identity_field_access(self):
        user_mind = UserMind(user_id="test_user")

        # Set and get identity fields
        user_mind.set_identity_field("style", "hunter")
        assert user_mind.get_identity_field("style") == "hunter"
        assert user_mind.get_identity_field("missing", "default") == "default"

    def test_pattern_access(self):
        user_mind = UserMind(user_id="test_user")

        user_mind.set_pattern("outreach", {"avg_touches": 4})
        assert user_mind.get_pattern("outreach") == {"avg_touches": 4}

    def test_increment_interactions(self):
        user_mind = UserMind(user_id="test_user")

        assert user_mind.total_interactions == 0
        user_mind.increment_interactions()
        assert user_mind.total_interactions == 1
        assert user_mind.last_interaction is not None


class TestProjectMind:
    def test_create_with_defaults(self):
        project_mind = ProjectMind(
            user_mind_id="user_mind_1",
            project_id="project_1"
        )

        assert project_mind.project_id == "project_1"
        assert project_mind.momentum_score == 0.5
        assert project_mind.interaction_count == 0
        assert project_mind.journey_stage is None
        assert project_mind.context_data == {}

    def test_context_field_access(self):
        project_mind = ProjectMind(
            user_mind_id="user_mind_1",
            project_id="project_1"
        )

        project_mind.set_context_field("deal_stage", "negotiating")
        assert project_mind.get_context_field("deal_stage") == "negotiating"

    def test_increment_interactions(self):
        project_mind = ProjectMind(
            user_mind_id="user_mind_1",
            project_id="project_1"
        )

        assert project_mind.interaction_count == 0
        project_mind.increment_interactions()
        assert project_mind.interaction_count == 1

    def test_update_momentum(self):
        project_mind = ProjectMind(
            user_mind_id="user_mind_1",
            project_id="project_1",
            momentum_score=0.5,
            days_since_activity=5
        )

        project_mind.update_momentum()
        assert project_mind.days_since_activity == 0
        assert project_mind.momentum_score == 0.6  # 0.5 + 0.1


class TestConversationMemory:
    def test_create_with_defaults(self):
        memory = ConversationMemory(project_mind_id="pm_1")

        assert memory.messages == []
        assert memory.summary is None

    def test_add_message(self):
        memory = ConversationMemory(project_mind_id="pm_1")

        memory.add_message("user", "Hello")
        memory.add_message("assistant", "Hi there!")

        assert len(memory.messages) == 2
        assert memory.messages[0].role == "user"
        assert memory.messages[0].content == "Hello"

    def test_get_recent_messages(self):
        memory = ConversationMemory(project_mind_id="pm_1")

        for i in range(15):
            memory.add_message("user", f"Message {i}")

        recent = memory.get_recent_messages(limit=5)
        assert len(recent) == 5
        assert recent[0].content == "Message 10"
        assert recent[4].content == "Message 14"

    def test_to_openai_messages(self):
        memory = ConversationMemory(project_mind_id="pm_1")
        memory.add_message("user", "Hello")
        memory.add_message("assistant", "Hi!")

        openai_format = memory.to_openai_messages()

        assert openai_format == [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"},
        ]
