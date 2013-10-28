use Test::More;

use FindBin;
use lib "$FindBin::Bin/../lib";

# use test
use_ok('Ditaa');

# constructor test
can_ok('Ditaa', 'new');

# image render test
my $d = Ditaa->new;
my $img = eval{$d->render_image('', '')};
ok $@, $@;

$d = Ditaa->new(
    bin => '/usr/bin/ditaa',
    java => '/usr/bin/java',
);

my $img = eval{$d->render_image(qq{
    +-----+
    |MyAPP|
    +-----+
}, "$FindBin::Bin/foo.png")};
ok !$@, "image render ok";

done_testing();
