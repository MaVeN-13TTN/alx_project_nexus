# Database Design - Entity Relationship Diagram (ERD)

## 🎯 ERD Overview

This document describes the database design for the Movie Recommendation Backend system. The ERD illustrates the relationships between entities and ensures data integrity while supporting efficient queries for movie recommendations.

## 📊 ERD Diagram

### Visual Representation

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│      User       │         │   UserFavorite  │         │     Movie       │
├─────────────────┤         ├─────────────────┤         ├─────────────────┤
│ id (PK)         │◄─────┐  │ id (PK)         │  ┌─────►│ id (PK)         │
│ username        │      │  │ user_id (FK)    │  │      │ tmdb_id (UNIQUE)│
│ email           │      └──┤ movie_id (FK)   │──┘      │ title           │
│ first_name      │         │ created_at      │         │ overview        │
│ last_name       │         └─────────────────┘         │ release_date    │
│ password        │                                     │ poster_path     │
│ is_active       │         ┌─────────────────┐         │ backdrop_path   │
│ date_joined     │         │ UserPreference  │         │ vote_average    │
│ created_at      │◄────────┤ id (PK)         │         │ vote_count      │
│ updated_at      │         │ user_id (FK)    │         │ runtime         │
└─────────────────┘         │ created_at      │         │ status          │
         │                  │ updated_at      │         │ created_at      │
         │                  └─────────────────┘         │ updated_at      │
         │                           │                  └─────────────────┘
         │                           │                           │
         │                  ┌─────────────────┐                 │
         │                  │PreferenceGenre  │                 │
         │                  ├─────────────────┤                 │
         │                  │ id (PK)         │                 │
         │                  │ preference_id   │◄────────────────┘
         │                  │ genre_id (FK)   │──┐              │
         │                  └─────────────────┘  │              │
         │                                       │              │
         │                  ┌─────────────────┐  │              │
         └──────────────────┤     Genre       │◄─┘              │
                            ├─────────────────┤                 │
                            │ id (PK)         │                 │
                            │ tmdb_id (UNIQUE)│                 │
                            │ name            │                 │
                            │ created_at      │                 │
                            └─────────────────┘                 │
                                     │                          │
                                     │                          │
                            ┌─────────────────┐                 │
                            │   MovieGenre    │                 │
                            ├─────────────────┤                 │
                            │ id (PK)         │                 │
                            │ movie_id (FK)   │◄────────────────┘
                            │ genre_id (FK)   │◄────────────────┐
                            └─────────────────┘                 │
                                                               │
                            ┌─────────────────┐                 │
                            │   MovieCast     │                 │
                            ├─────────────────┤                 │
                            │ id (PK)         │                 │
                            │ movie_id (FK)   │◄────────────────┘
                            │ person_id       │
                            │ character       │
                            │ order           │
                            │ cast_type       │
                            └─────────────────┘
```

## 🗃 Detailed Entity Descriptions

### 1. User Entity (Extended Django User)

**Purpose**: Store user account information and authentication details.

| Field Name  | Data Type  | Constraints       | Description                |
| ----------- | ---------- | ----------------- | -------------------------- |
| id          | Integer    | Primary Key, Auto | Unique user identifier     |
| username    | CharField  | Unique, Max 150   | User's unique username     |
| email       | EmailField | Unique            | User's email address       |
| first_name  | CharField  | Max 150, Optional | User's first name          |
| last_name   | CharField  | Max 150, Optional | User's last name           |
| password    | CharField  | Max 128           | Hashed password            |
| is_active   | Boolean    | Default True      | Account active status      |
| date_joined | DateTime   | Auto Now Add      | Account creation timestamp |
| created_at  | DateTime   | Auto Now Add      | Record creation timestamp  |
| updated_at  | DateTime   | Auto Now          | Record update timestamp    |

### 2. Movie Entity

**Purpose**: Store movie information retrieved from TMDb API.

| Field Name    | Data Type    | Constraints         | Description                    |
| ------------- | ------------ | ------------------- | ------------------------------ |
| id            | Integer      | Primary Key, Auto   | Unique movie identifier        |
| tmdb_id       | Integer      | Unique, Not Null    | TMDb movie ID                  |
| title         | CharField    | Max 255, Not Null   | Movie title                    |
| overview      | TextField    | Optional            | Movie plot summary             |
| release_date  | DateField    | Optional            | Movie release date             |
| poster_path   | CharField    | Max 255, Optional   | Poster image URL path          |
| backdrop_path | CharField    | Max 255, Optional   | Backdrop image URL path        |
| vote_average  | DecimalField | Max Digits 3, Dec 1 | Average user rating (0.0-10.0) |
| vote_count    | Integer      | Default 0           | Number of votes                |
| runtime       | Integer      | Optional            | Movie duration in minutes      |
| status        | CharField    | Max 50, Optional    | Release status                 |
| created_at    | DateTime     | Auto Now Add        | Record creation timestamp      |
| updated_at    | DateTime     | Auto Now            | Record update timestamp        |

### 3. Genre Entity

**Purpose**: Store movie genre categories.

| Field Name | Data Type | Constraints       | Description                 |
| ---------- | --------- | ----------------- | --------------------------- |
| id         | Integer   | Primary Key, Auto | Unique genre identifier     |
| tmdb_id    | Integer   | Unique, Not Null  | TMDb genre ID               |
| name       | CharField | Max 100, Not Null | Genre name (e.g., "Action") |
| created_at | DateTime  | Auto Now Add      | Record creation timestamp   |

### 4. UserFavorite Entity

**Purpose**: Track which movies users have marked as favorites.

| Field Name | Data Type  | Constraints       | Description                 |
| ---------- | ---------- | ----------------- | --------------------------- |
| id         | Integer    | Primary Key, Auto | Unique favorite identifier  |
| user       | ForeignKey | User, Cascade     | Reference to User           |
| movie      | ForeignKey | Movie, Cascade    | Reference to Movie          |
| created_at | DateTime   | Auto Now Add      | Favorite creation timestamp |

**Unique Constraint**: (user, movie) - Prevents duplicate favorites

### 5. UserPreference Entity

**Purpose**: Store user's genre preferences for personalized recommendations.

| Field Name | Data Type | Constraints       | Description                   |
| ---------- | --------- | ----------------- | ----------------------------- |
| id         | Integer   | Primary Key, Auto | Unique preference identifier  |
| user       | OneToOne  | User, Cascade     | Reference to User             |
| created_at | DateTime  | Auto Now Add      | Preference creation timestamp |
| updated_at | DateTime  | Auto Now          | Preference update timestamp   |

### 6. MovieGenre Entity (Junction Table)

**Purpose**: Many-to-many relationship between movies and genres.

| Field Name | Data Type  | Constraints       | Description                    |
| ---------- | ---------- | ----------------- | ------------------------------ |
| id         | Integer    | Primary Key, Auto | Unique relationship identifier |
| movie      | ForeignKey | Movie, Cascade    | Reference to Movie             |
| genre      | ForeignKey | Genre, Cascade    | Reference to Genre             |

**Unique Constraint**: (movie, genre) - Prevents duplicate genre assignments

### 7. PreferenceGenre Entity (Junction Table)

**Purpose**: Many-to-many relationship between user preferences and genres.

| Field Name | Data Type  | Constraints             | Description                    |
| ---------- | ---------- | ----------------------- | ------------------------------ |
| id         | Integer    | Primary Key, Auto       | Unique relationship identifier |
| preference | ForeignKey | UserPreference, Cascade | Reference to UserPreference    |
| genre      | ForeignKey | Genre, Cascade          | Reference to Genre             |

**Unique Constraint**: (preference, genre) - Prevents duplicate genre preferences

### 8. MovieCast Entity (Optional Enhancement)

**Purpose**: Store movie cast and crew information for advanced recommendations.

| Field Name | Data Type  | Constraints       | Description            |
| ---------- | ---------- | ----------------- | ---------------------- |
| id         | Integer    | Primary Key, Auto | Unique cast identifier |
| movie      | ForeignKey | Movie, Cascade    | Reference to Movie     |
| person_id  | Integer    | Not Null          | TMDb person ID         |
| character  | CharField  | Max 255, Optional | Character name         |
| order      | Integer    | Optional          | Cast order/importance  |
| cast_type  | CharField  | Max 50            | 'cast' or 'crew'       |

## 🔗 Relationship Details

### User ↔ Movie Relationships

1. **User Favorites** (Many-to-Many)

   - A user can have multiple favorite movies
   - A movie can be favorited by multiple users
   - Implemented through `UserFavorite` junction table

2. **User Preferences** (One-to-One)
   - Each user has one set of preferences
   - Preferences link to multiple genres

### Movie ↔ Genre Relationships

1. **Movie Genres** (Many-to-Many)
   - A movie can belong to multiple genres
   - A genre can be assigned to multiple movies
   - Implemented through `MovieGenre` junction table

### User ↔ Genre Relationships

1. **User Genre Preferences** (Many-to-Many)
   - A user can prefer multiple genres
   - A genre can be preferred by multiple users
   - Implemented through `PreferenceGenre` junction table

## 📈 Database Indexes

### Primary Indexes (Automatic)

- All primary keys automatically indexed

### Custom Indexes for Performance

```sql
-- User lookups
CREATE INDEX idx_user_username ON auth_user(username);
CREATE INDEX idx_user_email ON auth_user(email);

-- Movie lookups
CREATE INDEX idx_movie_tmdb_id ON movies_movie(tmdb_id);
CREATE INDEX idx_movie_title ON movies_movie(title);
CREATE INDEX idx_movie_release_date ON movies_movie(release_date);
CREATE INDEX idx_movie_vote_average ON movies_movie(vote_average);

-- Genre lookups
CREATE INDEX idx_genre_tmdb_id ON movies_genre(tmdb_id);
CREATE INDEX idx_genre_name ON movies_genre(name);

-- Relationship lookups
CREATE INDEX idx_userfavorite_user ON favorites_userfavorite(user_id);
CREATE INDEX idx_userfavorite_movie ON favorites_userfavorite(movie_id);
CREATE INDEX idx_moviegenre_movie ON movies_moviegenre(movie_id);
CREATE INDEX idx_moviegenre_genre ON movies_moviegenre(genre_id);

-- Timestamp indexes for analytics
CREATE INDEX idx_movie_created_at ON movies_movie(created_at);
CREATE INDEX idx_userfavorite_created_at ON favorites_userfavorite(created_at);
```

## 🎯 Query Optimization Strategies

### Common Query Patterns

1. **User's Favorite Movies**

   ```python
   user.favorites.select_related('movie').prefetch_related('movie__genres')
   ```

2. **Movies by Genre**

   ```python
   Movie.objects.filter(genres__name='Action').select_related().distinct()
   ```

3. **User Recommendations Based on Preferences**

   ```python
   preferred_genres = user.preference.genres.all()
   Movie.objects.filter(genres__in=preferred_genres).distinct()
   ```

4. **Trending Movies with Genres**
   ```python
   Movie.objects.prefetch_related('genres').order_by('-vote_average', '-vote_count')
   ```

### Database Normalization

The database design follows **Third Normal Form (3NF)**:

1. **First Normal Form**: All attributes contain atomic values
2. **Second Normal Form**: All non-key attributes depend on the entire primary key
3. **Third Normal Form**: No transitive dependencies exist

### Data Integrity Constraints

1. **Referential Integrity**: All foreign keys reference valid records
2. **Unique Constraints**: Prevent duplicate relationships and ensure data quality
3. **Check Constraints**: Validate data ranges (e.g., vote_average between 0-10)
4. **Not Null Constraints**: Ensure required fields are populated

## 🔄 Migration Strategy

### Initial Migration

```python
# 0001_initial.py - Create all base models
# 0002_add_indexes.py - Add performance indexes
# 0003_add_constraints.py - Add data integrity constraints
# 0004_sample_data.py - Load initial sample data (optional)
```

### Future Enhancements

- Additional movie metadata (budget, revenue, production companies)
- User rating system (separate from TMDb ratings)
- Movie review and comment system
- Advanced recommendation factors (watch history, rating patterns)
- Social features (friend recommendations, shared lists)

## 📝 Sample Data Scenarios

### Example Data Set

#### Users
```sql
INSERT INTO auth_user (username, email, first_name, last_name) VALUES
('moviefan123', 'fan@example.com', 'John', 'Doe'),
('cinephile', 'cinema@example.com', 'Jane', 'Smith'),
('actionlover', 'action@example.com', 'Mike', 'Johnson');
```

#### Movies
```sql
INSERT INTO movies_movie (tmdb_id, title, overview, release_date, vote_average, vote_count) VALUES
(550, 'Fight Club', 'A ticking-time-bomb insomniac...', '1999-10-15', 8.4, 26280),
(13, 'Forrest Gump', 'A man with a low IQ...', '1994-07-06', 8.8, 24000),
(155, 'The Dark Knight', 'Batman raises the stakes...', '2008-07-18', 9.0, 28000);
```

#### Genres
```sql
INSERT INTO movies_genre (tmdb_id, name) VALUES
(28, 'Action'), (18, 'Drama'), (53, 'Thriller'), (35, 'Comedy');
```

#### User Favorites
```sql
INSERT INTO favorites_userfavorite (user_id, movie_id) VALUES
(1, 1), (1, 3), (2, 1), (2, 2), (3, 3);
```

#### User Preferences
```sql
INSERT INTO preferences_userpreference (user_id) VALUES (1), (2), (3);
INSERT INTO preferences_preferencegenre (preference_id, genre_id) VALUES
(1, 1), (1, 3), (2, 2), (2, 4), (3, 1);
```

### Data Scenarios

1. **New User Journey**: User registers → Sets preferences → Browses movies → Adds favorites
2. **Recommendation Engine**: User with Action/Thriller preferences gets recommended similar movies
3. **Popular Content**: Movies with high vote_average and vote_count appear in trending
4. **Genre Analysis**: Users preferring Drama get personalized Drama movie recommendations

## 🔄 Backup & Recovery Strategy

### Database Backup
- **Daily automated backups** of PostgreSQL database
- **Point-in-time recovery** capability for data restoration
- **Cross-region backup replication** for disaster recovery
- **Backup retention policy**: 30 days daily, 12 months monthly

### Recovery Procedures
- **RTO (Recovery Time Objective)**: < 4 hours
- **RPO (Recovery Point Objective)**: < 1 hour data loss
- **Automated failover** to backup database instance
- **Regular backup restoration testing** to ensure data integrity

This ERD design provides a solid foundation for the movie recommendation system while maintaining flexibility for future enhancements and ensuring optimal query performance.
