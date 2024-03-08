def create_spatial_hash(cell_size):
    return {}

def get_spatial_hash_key(position, cell_size):
    return (int(position[0] // cell_size), int(position[1] // cell_size))

def update_spatial_hash(spatial_hash, sprites, cell_size):
    spatial_hash.clear()
    for sprite in sprites:
        key = get_spatial_hash_key(sprite.rect.center, cell_size)
        if key not in spatial_hash:
            spatial_hash[key] = [sprite]
        else:
            spatial_hash[key].append(sprite)

def get_nearby_sprites(spatial_hash, sprite, cell_size):
    center = sprite.rect.center  # Now extracting .rect.center from the sprite object
    key = get_spatial_hash_key(center, cell_size)
    nearby_sprites = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nearby_key = (key[0] + dx, key[1] + dy)
            nearby_sprites.extend(spatial_hash.get(nearby_key, []))
    return nearby_sprites
